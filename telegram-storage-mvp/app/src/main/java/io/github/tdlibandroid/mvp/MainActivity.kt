package io.github.tdlibandroid.mvp

import android.content.Context
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.animation.AnimatedContent
import androidx.compose.animation.ExperimentalAnimationApi
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.compose.ui.unit.dp
import io.github.tdlibandroid.ktx.TdClient
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.flow.launchIn
import kotlinx.coroutines.flow.onEach
import kotlinx.coroutines.launch
import org.drinkless.tdlib.TdApi

class MainActivity : ComponentActivity() {
    private var tdClient: TdClient? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        
        val prefs = getSharedPreferences("crash_prefs", Context.MODE_PRIVATE)
        val lastCrash = prefs.getString("last_crash", null)
        
        Thread.setDefaultUncaughtExceptionHandler { _, e ->
            prefs.edit().putString("last_crash", e.stackTraceToString()).commit()
            kotlin.system.exitProcess(1)
        }

        try {
            System.loadLibrary("tdjni")
        } catch (e: Throwable) {
            prefs.edit().putString("last_crash", "Library load failed: ${e.stackTraceToString()}").commit()
        }

        setContent {
            MaterialTheme(colorScheme = darkColorScheme()) {
                Surface(
                    modifier = Modifier.fillMaxSize(),
                    color = MaterialTheme.colorScheme.background
                ) {
                    if (lastCrash != null) {
                        CrashScreen(lastCrash) {
                            prefs.edit().remove("last_crash").apply()
                            recreate()
                        }
                    } else {
                        TelegramApp(filesDir.absolutePath) { client ->
                            tdClient = client
                        }
                    }
                }
            }
        }
    }

    override fun onDestroy() {
        super.onDestroy()
        tdClient?.close()
    }
}

@Composable
fun CrashScreen(crashText: String, onClear: () -> Unit) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp)
            .verticalScroll(rememberScrollState())
    ) {
        Text("App Crashed!", style = MaterialTheme.typography.headlineMedium, color = MaterialTheme.colorScheme.error)
        Spacer(Modifier.height(16.dp))
        Text(crashText, style = MaterialTheme.typography.bodySmall)
        Spacer(Modifier.height(24.dp))
        Button(onClick = onClear) {
            Text("Clear & Restart")
        }
    }
}

enum class AuthStep {
    API_KEYS, PHONE, CODE, PASSWORD, LOGGED_IN
}

@OptIn(ExperimentalAnimationApi::class)
@Composable
fun TelegramApp(filesDir: String, onClientReady: (TdClient) -> Unit) {
    var authStep by remember { mutableStateOf(AuthStep.API_KEYS) }
    var apiId by remember { mutableStateOf("") }
    var apiHash by remember { mutableStateOf("") }
    var tdClient by remember { mutableStateOf<TdClient?>(null) }
    var errorText by remember { mutableStateOf("") }
    val scope = rememberCoroutineScope()

    // Listen to Authorization State
    LaunchedEffect(tdClient) {
        tdClient?.updates?.onEach { update ->
            if (update is TdApi.UpdateAuthorizationState) {
                when (update.authorizationState) {
                    is TdApi.AuthorizationStateWaitPhoneNumber -> authStep = AuthStep.PHONE
                    is TdApi.AuthorizationStateWaitCode -> authStep = AuthStep.CODE
                    is TdApi.AuthorizationStateWaitPassword -> authStep = AuthStep.PASSWORD
                    is TdApi.AuthorizationStateReady -> authStep = AuthStep.LOGGED_IN
                }
            }
        }?.launchIn(this)
    }

    AnimatedContent(targetState = authStep, label = "Auth Transition") { step ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(24.dp)
                .verticalScroll(rememberScrollState()),
            verticalArrangement = Arrangement.Center,
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            if (errorText.isNotEmpty()) {
                Text(errorText, color = MaterialTheme.colorScheme.error)
                Spacer(modifier = Modifier.height(16.dp))
            }

            when (step) {
                AuthStep.API_KEYS -> {
                    Text("Telegram API Configuration", style = MaterialTheme.typography.headlineMedium)
                    Spacer(modifier = Modifier.height(16.dp))
                    OutlinedTextField(
                        value = apiId,
                        onValueChange = { apiId = it },
                        label = { Text("API ID") },
                        keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
                        modifier = Modifier.fillMaxWidth()
                    )
                    Spacer(modifier = Modifier.height(8.dp))
                    OutlinedTextField(
                        value = apiHash,
                        onValueChange = { apiHash = it },
                        label = { Text("API Hash") },
                        modifier = Modifier.fillMaxWidth()
                    )
                    Spacer(modifier = Modifier.height(24.dp))
                    Button(
                        onClick = {
                            errorText = ""
                            try {
                                val parsedId = apiId.trim().toIntOrNull()
                                if (parsedId == null) {
                                    errorText = "Invalid API ID (must be a number)"
                                    return@Button
                                }
                                val client = TdClient(filesDir, 1, parsedId, apiHash.trim())
                                client.init()
                                tdClient = client
                                onClientReady(client)
                            } catch (e: Exception) {
                                errorText = "Init failed: ${e.message}"
                            } catch (e: Error) {
                                errorText = "Init Error (Native?): ${e.message}"
                            }
                        },
                        modifier = Modifier.fillMaxWidth(),
                        shape = RoundedCornerShape(8.dp)
                    ) {
                        Text("Initialize TDLib")
                    }
                }
                AuthStep.PHONE -> {
                    var phone by remember { mutableStateOf("") }
                    Text("Sign In", style = MaterialTheme.typography.headlineMedium)
                    Spacer(modifier = Modifier.height(16.dp))
                    OutlinedTextField(
                        value = phone,
                        onValueChange = { phone = it },
                        label = { Text("Phone Number (with +)") },
                        keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Phone),
                        modifier = Modifier.fillMaxWidth()
                    )
                    Spacer(modifier = Modifier.height(24.dp))
                    Button(
                        onClick = {
                            errorText = ""
                            scope.launch {
                                try {
                                    tdClient?.send(TdApi.SetAuthenticationPhoneNumber(phone.trim(), null))
                                } catch (e: Exception) {
                                    errorText = "Error: ${e.message}"
                                }
                            }
                        },
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        Text("Send Code")
                    }
                }
                AuthStep.CODE -> {
                    var code by remember { mutableStateOf("") }
                    Text("Verification", style = MaterialTheme.typography.headlineMedium)
                    Spacer(modifier = Modifier.height(16.dp))
                    OutlinedTextField(
                        value = code,
                        onValueChange = { code = it },
                        label = { Text("Enter Code") },
                        keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
                        modifier = Modifier.fillMaxWidth()
                    )
                    Spacer(modifier = Modifier.height(24.dp))
                    Button(
                        onClick = {
                            errorText = ""
                            scope.launch {
                                try {
                                    tdClient?.send(TdApi.CheckAuthenticationCode(code.trim()))
                                } catch (e: Exception) {
                                    errorText = "Error: ${e.message}"
                                }
                            }
                        },
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        Text("Verify Code")
                    }
                }
                AuthStep.PASSWORD -> {
                    var password by remember { mutableStateOf("") }
                    Text("Two-Step Verification", style = MaterialTheme.typography.headlineMedium)
                    Spacer(modifier = Modifier.height(16.dp))
                    OutlinedTextField(
                        value = password,
                        onValueChange = { password = it },
                        label = { Text("2FA Password") },
                        visualTransformation = PasswordVisualTransformation(),
                        keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Password),
                        modifier = Modifier.fillMaxWidth()
                    )
                    Spacer(modifier = Modifier.height(24.dp))
                    Button(
                        onClick = {
                            errorText = ""
                            scope.launch {
                                try {
                                    tdClient?.send(TdApi.CheckAuthenticationPassword(password))
                                } catch (e: Exception) {
                                    errorText = "Error: ${e.message}"
                                }
                            }
                        },
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        Text("Submit Password")
                    }
                }
                AuthStep.LOGGED_IN -> {
                    var myId by remember { mutableStateOf<Long?>(null) }

                    LaunchedEffect(Unit) {
                        try {
                            val me = tdClient?.send(TdApi.GetMe())
                            myId = me?.id
                        } catch (e: Exception) {
                            errorText = "Failed to get User ID: ${e.message}"
                        }
                    }

                    Text("Welcome to Telegram Storage!", style = MaterialTheme.typography.headlineMedium)
                    Spacer(modifier = Modifier.height(16.dp))
                    Text("You are successfully authenticated.", style = MaterialTheme.typography.bodyLarge)
                    Spacer(modifier = Modifier.height(32.dp))
                    
                    if (myId != null) {
                        Button(
                            onClick = {
                                errorText = ""
                                scope.launch {
                                    try {
                                        val content = TdApi.InputMessageText(
                                            TdApi.FormattedText("Hello from TDLib MVP Storage App!", emptyArray()),
                                            null,
                                            true
                                        )
                                        tdClient?.send(TdApi.SendMessage(myId!!, null, null, null, null, content))
                                        errorText = "Message sent to Saved Messages!"
                                    } catch (e: Exception) {
                                        errorText = "Send failed: ${e.message}"
                                    }
                                }
                            },
                            modifier = Modifier.fillMaxWidth()
                        ) {
                            Text("Send Test Message to Saved Messages")
                        }
                    } else {
                        CircularProgressIndicator()
                    }
                }
            }
        }
    }
}
