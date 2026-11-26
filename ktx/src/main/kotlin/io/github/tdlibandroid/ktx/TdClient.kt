package io.github.tdlibandroid.ktx

import kotlinx.coroutines.*
import kotlinx.coroutines.channels.Channel
import kotlinx.coroutines.flow.*
import org.drinkless.tdlib.Client
import org.drinkless.tdlib.TdApi
import java.util.concurrent.ConcurrentHashMap
import java.util.concurrent.atomic.AtomicBoolean
import java.util.concurrent.atomic.AtomicLong

/**
 * Kotlin Coroutines wrapper for TDLib.
 * Thread-safe. Lifecycle-aware. Zero opinion on auth or app structure.
 *
 * Usage:
 *   val client = TdClient(filesDir = context.filesDir.absolutePath + "/tdlib")
 *   client.init()
 *   client.updates.collect { update -> /* handle update */ }
 *   val option = client.send(TdApi.GetOption("version"))
 *   client.close()
 */
class TdClient(
    private val filesDir: String,
    private val verbosityLevel: Int = 0,   // 0=FATAL, 1=ERROR, 2=WARN, 5=DEBUG
    private val apiId: Int = 0,
    private val apiHash: String = "",
    private val dispatcher: CoroutineDispatcher = Dispatchers.IO
) {
    private val scope = CoroutineScope(SupervisorJob() + dispatcher)

    // Update stream — hot SharedFlow, 0 replay (stateless), unlimited buffer
    private val _updates = MutableSharedFlow<TdApi.Update>(
        extraBufferCapacity = Channel.UNLIMITED
    )
    val updates: SharedFlow<TdApi.Update> = _updates.asSharedFlow()

    // Error stream for async initialization / background TDLib errors
    private val _errors = MutableSharedFlow<Throwable>(
        extraBufferCapacity = Channel.UNLIMITED
    )
    val errors: SharedFlow<Throwable> = _errors.asSharedFlow()

    // Pending request map: requestId → CompletableDeferred<TdApi.Object>
    private val pending = ConcurrentHashMap<Long, CompletableDeferred<TdApi.Object>>()
    private val requestId = AtomicLong(0)
    private val initialized = AtomicBoolean(false)
    private val initDeferred = CompletableDeferred<Unit>()

    @Volatile
    private var nativeClient: Client? = null

    /**
     * Initialize TDLib. Must be called before any send().
     * Safe to call multiple times; subsequent calls are no-ops.
     * Sets up native client, log level, and database path.
     */
    fun init() {
        if (!initialized.compareAndSet(false, true)) return

        try {
            Client.execute(TdApi.SetLogVerbosityLevel(verbosityLevel))
        } catch (e: Exception) {
            println("[TdClient] Failed to set log verbosity level: $e")
        }
        nativeClient = Client.create(
            { update ->
                if (update is TdApi.Update) {
                    _updates.tryEmit(update)
                }
            },
            { throwable ->
                // Update exception handler — log, don't crash
                println("[TdClient] Update exception: $throwable")
            },
            { throwable ->
                // Default exception handler
                println("[TdClient] Default exception: $throwable")
            }
        )

        // Set TDLib database directory
        scope.launch {
            try {
                send(TdApi.SetTdlibParameters(
                    /* useTestDc = */ false,
                    /* databaseDirectory = */ filesDir,
                    /* filesDirectory = */ "$filesDir/files",
                    /* databaseEncryptionKey = */ ByteArray(0),
                    /* useFileDatabase = */ true,
                    /* useChatInfoDatabase = */ true,
                    /* useMessageDatabase = */ true,
                    /* useSecretChats = */ false,
                    /* apiId = */ apiId,
                    /* apiHash = */ apiHash,
                    /* systemLanguageCode = */ "en",
                    /* deviceModel = */ android.os.Build.MODEL,
                    /* systemVersion = */ android.os.Build.VERSION.RELEASE,
                    /* applicationVersion = */ "1.0"
                ))
                initDeferred.complete(Unit)
            } catch (e: CancellationException) {
                throw e
            } catch (e: Exception) {
                _errors.tryEmit(e)
                initDeferred.completeExceptionally(e)
                println("[TdClient] Failed to set parameters: $e")
            }
        }
    }

    /**
     * Suspends until initial SetTdlibParameters completes, or rethrows any initialization error.
     */
    suspend fun awaitInit() {
        initDeferred.await()
    }

    /**
     * Send a TDLib function and suspend until response arrives.
     * Throws TdException on TdApi.Error response.
     * Thread-safe — can be called from any coroutine.
     *
     * @throws IllegalStateException if init() has not been called or client is closed
     * @throws TdException if TDLib returns TdApi.Error
     * @throws CancellationException if coroutine is cancelled before response
     */
    @Suppress("UNCHECKED_CAST")
    suspend fun <T : TdApi.Object> send(function: TdApi.Function<T>): T {
        val client = nativeClient
            ?: throw IllegalStateException("TdClient not initialized. Call init() first.")

        val id = requestId.incrementAndGet()
        val deferred = CompletableDeferred<TdApi.Object>()
        pending[id] = deferred
        deferred.invokeOnCompletion { pending.remove(id) }

        try {
            client.send(function) { result ->
                when (result) {
                    is TdApi.Error -> deferred.completeExceptionally(
                        TdException(result.code, result.message)
                    )
                    else -> deferred.complete(result)
                }
            }
        } catch (t: Throwable) {
            pending.remove(id)
            throw t
        }

        return deferred.await() as T
    }

    /**
     * Close TDLib client and release all resources.
     * After close(), this instance cannot be reused.
     */
    fun close() {
        try {
            nativeClient?.send(TdApi.Close(), null, null)
        } catch (e: Exception) {
            println("[TdClient] Failed to send Close command: $e")
        }
        initDeferred.cancel(CancellationException("TdClient closed"))
        scope.cancel()
        nativeClient = null
        pending.forEach { (_, deferred) ->
            deferred.completeExceptionally(CancellationException("TdClient closed"))
        }
        pending.clear()
    }

    internal fun emitUpdate(update: TdApi.Update): Boolean = _updates.tryEmit(update)

    internal fun pendingCount(): Int = pending.size
}

/**
 * Exception thrown when TDLib returns TdApi.Error.
 */
class TdException(val code: Int, override val message: String) : Exception(message) {
    val isFloodWait: Boolean get() = message.startsWith("FLOOD_WAIT_")
    val floodWaitSeconds: Long get() = if (isFloodWait) message.removePrefix("FLOOD_WAIT_").trim().toLongOrNull() ?: 0L else 0L
    val isUnauthorized: Boolean get() = code == 401
}

/**
 * Returns a Flow of authorization states.
 */
fun TdClient.authStateFlow(): Flow<TdApi.AuthorizationState> =
    updates.filterIsInstance<TdApi.UpdateAuthorizationState>().map { it.authorizationState }

/**
 * Suspends until TDLib reaches AuthorizationStateReady.
 */
suspend fun TdClient.awaitReady() {
    authStateFlow().filter { it is TdApi.AuthorizationStateReady }.first()
}

/**
 * Returns a Flow of a specific update type.
 */
inline fun <reified T : TdApi.Update> TdClient.updatesOf(): Flow<T> =
    updates.filterIsInstance<T>()

/**
 * Returns a Flow that tracks the progress of a specific file download/upload.
 * The flow completes automatically when the file transfer finishes.
 */
fun TdClient.trackFile(fileId: Int): Flow<TdApi.File> =
    updatesOf<TdApi.UpdateFile>()
        .map { it.file }
        .filter { it.id == fileId }
        .transformWhile {
            emit(it)
            it.local.isDownloadingActive || it.remote.isUploadingActive
        }
