# tdlib-android


**The only community-maintained TDLib distribution for Android. Auto-updated. Zero build steps.**

One Gradle line. No compiling TDLib from source. No GitHub token. No `.so` wrangling.
Works with any Telegram client, bot UI, or MTProto-based Android app.

## Setup

```kotlin
// settings.gradle.kts — nothing special, mavenCentral() already there

// build.gradle.kts (app)
dependencies {
    // Prebuilt TDLib — all 4 ABIs included
    implementation("io.github.tdlib-android:core:1.8.64")
    // Kotlin Coroutines + Flow wrapper (optional)
    implementation("io.github.tdlib-android:ktx:1.8.64")
}
```

That's it.

## ABI Coverage

| ABI | Devices |
|---|---|
| `arm64-v8a` | All modern Android (2016+) |
| `armeabi-v7a` | 32-bit ARM devices |
| `x86_64` | Android emulators (recommended for CI) |
| `x86` | Legacy emulators |

**Tested on:** Realme GT 7 (Dimensity 9400e) · Android 16 (API 36)

## Why this exists

Every other option as of 2026:
- up9cloud/android-libtdjson — frozen at 1.8.52, GitHub token required, raw .so only
- TGX-Android/tdlib — explicitly not for external use
- tdlibx/td-ktx — archived 2024, dead
- Build it yourself — broken on macOS, 45min Docker build, CI setup hours

This project automates the entire thing. CI polls upstream every 6 hours, builds for all ABIs, and publishes to Maven Central on new TDLib versions. You get a PR to review with the API diff before publish. One merge. Done.

## Usage Guide

### 1. Dependency Configuration
Ensure `mavenCentral()` is defined in your repository list, then add the core prebuilt JNI library and the optional Kotlin Coroutines/Flow extension to your `build.gradle.kts`:

```kotlin
// settings.gradle.kts
dependencyResolutionManagement {
    repositories {
        google()
        mavenCentral()
    }
}

// app/build.gradle.kts
dependencies {
    // Precompiled TDLib native C++ library (arm64-v8a, armeabi-v7a, x86_64, x86)
    implementation("io.github.tdlib-android:core:1.8.64")
    
    // Kotlin Coroutines + Flow wrapper (optional)
    implementation("io.github.tdlib-android:ktx:1.8.64")
}
```

### 2. Initialization & Usage
Load the native JNI library and initialize `TdClient` with your database path and Telegram API credentials:

```kotlin
import io.github.tdlibandroid.ktx.TdClient
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch

// Load the prebuilt native JNI library
System.loadLibrary("tdjni")

// Instantiate client with database path and API credentials
val filesDir = context.filesDir.absolutePath + "/tdlib"
val client = TdClient(
    filesDir = filesDir,
    verbosityLevel = 1,                     // 1 = Error/Fatal, 5 = Debug
    apiId = BuildConfig.TELEGRAM_API_ID,   // Load securely
    apiHash = BuildConfig.TELEGRAM_API_HASH // Load securely
)

client.init()

CoroutineScope(Dispatchers.IO).launch {
    client.updates.collect { update ->
        // Handle incoming MTProto updates reactively
    }
}
```

---

## Author & Credits

Created and maintained by **[Akash Priyadarshi (@AkashPriyadarshii)](https://github.com/AkashPriyadarshii)** to eliminate the complexity of manually compiling TDLib from source for multiple Android architectures. Custom Docker matrix builds and automated upstream workflows provide the global Android ecosystem with an up-to-date, zero-maintenance precompiled TDLib AAR.

---

## Version History

Auto-generated from TDLib upstream. See [CHANGELOG.md](CHANGELOG.md).

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) — CI architecture, ABI builds, and contributing guidelines.

## License

- TDLib binary and Java interfaces: **Boost Software License 1.0 (BSL-1.0)**.
- `ktx` wrapper module: **Apache License 2.0**.


