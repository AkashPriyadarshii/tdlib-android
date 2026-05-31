package io.github.tdlibandroid.sample

import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import io.github.tdlibandroid.ktx.TdClient
import io.github.tdlibandroid.ktx.awaitReady
import kotlinx.coroutines.flow.collect
import kotlinx.coroutines.launch
import org.drinkless.tdlib.TdApi

/**
 * Minimal sample app demonstrating tdlib-android:ktx wrapper usage.
 * Flow: initialize -> observe states -> authenticate -> get option.
 */
class MainActivity : AppCompatActivity() {

    private lateinit var client: TdClient

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        
        // Initialize client specifying database path
        client = TdClient(filesDir = filesDir.absolutePath + "/tdlib")
        client.init()

        // 1. Collect all update streams in background scope
        lifecycleScope.launch {
            client.updates.collect { update ->
                println("[SampleApp] Received update: ${update.javaClass.simpleName}")
                handleAuthStates(update)
            }
        }
        
        // 2. Fetch basic system info post auth completion
        lifecycleScope.launch {
            try {
                client.awaitReady()
                println("[SampleApp] TDLib client is Ready!")
                
                // Get Option "version" from JNI
                val response = client.send(TdApi.GetOption("version"))
                if (response is TdApi.OptionValueString) {
                    println("[SampleApp] Connected to TDLib version: ${response.value}")
                }
            } catch (e: Exception) {
                println("[SampleApp] Error during option fetch: $e")
            }
        }
    }

    /**
     * Handle authorization states requested by JNI wrapper.
     */
    private suspend fun handleAuthStates(update: TdApi.Update) {
        if (update is TdApi.UpdateAuthorizationState) {
            when (val state = update.authorizationState) {
                is TdApi.AuthorizationStateWaitPhoneNumber -> {
                    // Send phone number (in actual apps, prompt user here)
                    println("[SampleApp] State: Waiting for phone number. Send via client.send(...)")
                }
                is TdApi.AuthorizationStateWaitCode -> {
                    // Send verification code (in actual apps, prompt user here)
                    println("[SampleApp] State: Waiting for OTP code.")
                }
                is TdApi.AuthorizationStateReady -> {
                    println("[SampleApp] State: Authorized successfully.")
                }
                is TdApi.AuthorizationStateLoggingOut -> {
                    println("[SampleApp] State: Logging out.")
                }
                is TdApi.AuthorizationStateClosing -> {
                    println("[SampleApp] State: Closing.")
                }
                is TdApi.AuthorizationStateClosed -> {
                    println("[SampleApp] State: Closed.")
                }
            }
        }
    }

    override fun onDestroy() {
        super.onDestroy()
        // Release resources
        client.close()
    }
}
