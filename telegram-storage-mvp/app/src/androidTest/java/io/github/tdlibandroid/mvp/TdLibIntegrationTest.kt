package io.github.tdlibandroid.mvp

import androidx.test.ext.junit.runners.AndroidJUnit4
import androidx.test.platform.app.InstrumentationRegistry
import io.github.tdlibandroid.ktx.TdClient
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.runBlocking
import org.drinkless.tdlib.TdApi
import org.junit.Assert.assertTrue
import org.junit.Test
import org.junit.runner.RunWith

@RunWith(AndroidJUnit4::class)
class TdLibIntegrationTest {

    @Test
    fun testNativeLibraryLoadsAndConnects() = runBlocking {
        // Context of the app under test.
        val appContext = InstrumentationRegistry.getInstrumentation().targetContext
        val filesDir = appContext.filesDir.absolutePath

        // Load credentials dynamically from asset secrets.properties
        var apiId = 0
        var apiHash = ""
        try {
            val properties = java.util.Properties()
            appContext.assets.open("secrets.properties").use { properties.load(it) }
            apiId = properties.getProperty("apiId")?.trim()?.toIntOrNull() ?: 0
            apiHash = properties.getProperty("apiHash")?.trim() ?: ""
        } catch (e: Exception) {
            println("No secrets.properties asset found: $e")
        }

        assertTrue(
            "API ID and API Hash must be supplied in assets/secrets.properties for this integration test to run.",
            apiId != 0 && apiHash.isNotEmpty()
        )

        // Manually load the native library, just like the app does
        System.loadLibrary("tdjni")

        // Initialize TDLib wrapper
        val client = TdClient(filesDir, verbosityLevel = 1, apiId = apiId, apiHash = apiHash)
        client.init()

        // Wait for the first Authorization State from Telegram's cloud
        val update = client.updates.first { 
            it is TdApi.UpdateAuthorizationState 
        } as TdApi.UpdateAuthorizationState

        // If it successfully reaches this point and asks for a Phone Number, 
        // it means the C++ native library loaded, successfully communicated via JNI,
        // and established a secure connection to Telegram servers using the API ID/Hash.
        assertTrue(
            "Expected to wait for phone number or bot token",
            update.authorizationState is TdApi.AuthorizationStateWaitPhoneNumber
        )

        client.close()
    }
}
