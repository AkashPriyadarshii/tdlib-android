package io.github.tdlibandroid.ktx

import kotlinx.coroutines.flow.*
import org.drinkless.tdlib.TdApi

/**
 * Suspend until TDLib reaches authorizationStateReady.
 * Collect updates until ready, then return.
 */
suspend fun TdClient.awaitReady() {
    updates
        .filterIsInstance<TdApi.UpdateAuthorizationState>()
        .filter { it.authorizationState is TdApi.AuthorizationStateReady }
        .first()
}

/**
 * Returns a Flow of a specific update type.
 * Example: client.updatesOf<TdApi.UpdateNewMessage>().collect { ... }
 */
inline fun <reified T : TdApi.Update> TdClient.updatesOf(): Flow<T> =
    updates.filterIsInstance<T>()

/**
 * Returns true if TDLib is currently in authorizationStateReady.
 * Non-suspending — checks the last seen update state.
 * Note: for reliable state, prefer collecting updates directly.
 */
fun TdApi.AuthorizationState.isReady(): Boolean =
    this is TdApi.AuthorizationStateReady
