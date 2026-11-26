package io.github.tdlibandroid.ktx

import kotlinx.coroutines.CompletableDeferred
import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.flow.take
import kotlinx.coroutines.flow.toList
import kotlinx.coroutines.launch
import kotlinx.coroutines.test.UnconfinedTestDispatcher
import kotlinx.coroutines.test.runTest
import org.drinkless.tdlib.TdApi
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

@OptIn(ExperimentalCoroutinesApi::class)
class TdClientTest {

    @Test
    fun sendBeforeInitThrowsAndDoesNotLeakPending() = runTest {
        val client = TdClient(filesDir = "/tmp/tdlib-test", dispatcher = UnconfinedTestDispatcher(testScheduler))
        var threw = false
        try {
            client.send(TdApi.GetOption("version"))
        } catch (e: IllegalStateException) {
            threw = true
        }
        assertTrue(threw)
        assertEquals(0, client.pendingCount())
        client.close()
    }

    @Test
    fun closeBeforeInitIsSafe() {
        val client = TdClient(filesDir = "/tmp/tdlib-test")
        client.close()
        assertEquals(0, client.pendingCount())
    }

    @Test
    fun authStateFlowFiltersAndMapsAuthUpdates() = runTest {
        val client = TdClient(filesDir = "/tmp/tdlib-test", dispatcher = UnconfinedTestDispatcher(testScheduler))
        val states = mutableListOf<TdApi.AuthorizationState>()
        val job = launch(UnconfinedTestDispatcher(testScheduler)) {
            client.authStateFlow().take(2).toList(states)
        }

        client.emitUpdate(TdApi.UpdateOption().apply { name = "ignored" })
        client.emitUpdate(TdApi.UpdateAuthorizationState().apply {
            authorizationState = TdApi.AuthorizationStateWaitPhoneNumber()
        })
        client.emitUpdate(TdApi.UpdateAuthorizationState().apply {
            authorizationState = TdApi.AuthorizationStateReady()
        })

        job.join()
        assertEquals(2, states.size)
        assertTrue(states[0] is TdApi.AuthorizationStateWaitPhoneNumber)
        assertTrue(states[1] is TdApi.AuthorizationStateReady)
        client.close()
    }

    @Test
    fun awaitReadySuspendsUntilAuthorizationStateReady() = runTest {
        val client = TdClient(filesDir = "/tmp/tdlib-test", dispatcher = UnconfinedTestDispatcher(testScheduler))
        val ready = CompletableDeferred<Unit>()
        val job = launch(UnconfinedTestDispatcher(testScheduler)) {
            client.awaitReady()
            ready.complete(Unit)
        }

        client.emitUpdate(TdApi.UpdateAuthorizationState().apply {
            authorizationState = TdApi.AuthorizationStateWaitPhoneNumber()
        })
        assertFalse(ready.isCompleted)

        client.emitUpdate(TdApi.UpdateAuthorizationState().apply {
            authorizationState = TdApi.AuthorizationStateReady()
        })
        job.join()
        assertTrue(ready.isCompleted)
        client.close()
    }

    @Test
    fun updatesOfFiltersByUpdateType() = runTest {
        val client = TdClient(filesDir = "/tmp/tdlib-test", dispatcher = UnconfinedTestDispatcher(testScheduler))
        val options = mutableListOf<TdApi.UpdateOption>()
        val job = launch(UnconfinedTestDispatcher(testScheduler)) {
            client.updatesOf<TdApi.UpdateOption>().take(1).toList(options)
        }

        client.emitUpdate(TdApi.UpdateAuthorizationState().apply {
            authorizationState = TdApi.AuthorizationStateWaitPhoneNumber()
        })
        client.emitUpdate(TdApi.UpdateOption().apply { name = "version" })

        job.join()
        assertEquals(1, options.size)
        assertEquals("version", options[0].name)
        client.close()
    }

    @Test
    fun trackFileEmitsFinalCompletedUpdateAndCompletes() = runTest {
        val client = TdClient(filesDir = "/tmp/tdlib-test", dispatcher = UnconfinedTestDispatcher(testScheduler))
        val tracked = mutableListOf<TdApi.File>()
        val job = launch(UnconfinedTestDispatcher(testScheduler)) {
            client.trackFile(fileId = 42).toList(tracked)
        }

        // Unrelated file id is ignored
        client.emitUpdate(TdApi.UpdateFile().apply {
            file = TdApi.File().apply {
                id = 99
                local = TdApi.LocalFile().apply { isDownloadingActive = true }
                remote = TdApi.RemoteFile().apply { isUploadingActive = false }
            }
        })
        // Active download update
        client.emitUpdate(TdApi.UpdateFile().apply {
            file = TdApi.File().apply {
                id = 42
                local = TdApi.LocalFile().apply { isDownloadingActive = true }
                remote = TdApi.RemoteFile().apply { isUploadingActive = false }
            }
        })
        // Final completed update must still be emitted before flow completes
        client.emitUpdate(TdApi.UpdateFile().apply {
            file = TdApi.File().apply {
                id = 42
                local = TdApi.LocalFile().apply { isDownloadingActive = false }
                remote = TdApi.RemoteFile().apply { isUploadingActive = false }
            }
        })

        job.join()
        assertEquals(2, tracked.size)
        assertTrue(tracked[0].local.isDownloadingActive)
        assertFalse(tracked[1].local.isDownloadingActive)
        assertFalse(tracked[1].remote.isUploadingActive)
        client.close()
    }
}
