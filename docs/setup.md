# Set Up TDLib on Android in 3 Steps

> Add TDLib to any Android project via a prebuilt 4-ABI AAR. No local NDK, no compiling C++ from source.

## Prerequisites

Obtain an `api_id` and `api_hash` by registering an application at [my.telegram.org](https://my.telegram.org). Store these securely in `local.properties` or environment variables and expose them through `BuildConfig`.

---

## Step 1 — Add Dependencies

Configure `settings.gradle.kts`:
```kotlin
dependencyResolutionManagement {
    repositories {
        google()
        mavenCentral()
    }
}
```

Add the prebuilt AAR and Kotlin wrapper to `app/build.gradle.kts`:
```kotlin
dependencies {
    implementation("io.github.tdlib-android:core:0.1.0")
    implementation("io.github.tdlib-android:ktx:0.1.0")
}
```

To restrict packaged ABIs (e.g. for split APKs), set `abiFilters` in `defaultConfig`:
```kotlin
android {
    defaultConfig {
        ndk {
            abiFilters += listOf("arm64-v8a", "armeabi-v7a", "x86_64", "x86")
        }
    }
}
```

---

## Step 2 — Configure ProGuard / R8

The `:core` AAR embeds `consumer-rules.pro` automatically. If using custom obfuscation rules, ensure the native symbols are kept:
```proguard
# Keep TDLib JNI bridge and generated API classes
-keep class org.drinkless.tdlib.** { *; }
-keepclassmembers class org.drinkless.tdlib.** { *; }
-dontwarn org.drinkless.tdlib.**
```

---

## Step 3 — Load Native Library & Initialize

```kotlin
import java.io.File
import org.drinkless.tdlib.TdApi
import io.github.tdlib.ktx.TdClient
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch

// 1. Load native JNI binaries
System.loadLibrary("tdjni")

// 2. Initialize TdClient with isolated app storage
val client = TdClient(
    filesDir = File(context.filesDir, "tdlib").absolutePath,
    verbosityLevel = 1
)
client.init()

// 3. Collect MTProto updates reactively via Flow
CoroutineScope(Dispatchers.IO).launch {
    client.updates.collect { update ->
        when (update) {
            is TdApi.UpdateAuthorizationState -> {
                // handle authorization state transitions
            }
            is TdApi.UpdateNewMessage -> {
                // handle incoming MTProto messages
            }
        }
    }
}
```

---

## Android 15 & 16 KB Page Alignment

All binaries in `tdlib-android` are compiled with Android NDK 27+ with maximum page size alignment (`-Wl,-z,max-page-size=16384`), fully compliant with Google Play's 16 KB page size requirements for Android 15 devices.

- **Supported ABIs:** `arm64-v8a`, `armeabi-v7a`, `x86_64`, `x86`
- **Minimum Android SDK:** API 26 (Android 8.0 Oreo)
- **Zero Local Compilation:** Standard Maven Central dependency
