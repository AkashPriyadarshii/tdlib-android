# tdlib-android

[![TDLib Version](https://img.shields.io/badge/TDLib-1.8.64-blue)](https://github.com/tdlib/td)
[![Maven Central](https://img.shields.io/maven-central/v/io.github.tdlib-android/core)](https://central.sonatype.com/artifact/io.github.tdlib-android/core)
[![CI](https://github.com/tdlib-android/tdlib-android/actions/workflows/check-upstream.yml/badge.svg)](https://github.com/tdlib-android/tdlib-android/actions)
[![License](https://img.shields.io/badge/license-BSL--1.0-green)](LICENSE)

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

**Tested on:** Realme GT 7 (Dimensity 9400e) · Android 16 (API 36) ✓

## Why this exists

Every other option as of 2026:
- up9cloud/android-libtdjson — frozen at 1.8.52, GitHub token required, raw .so only
- TGX-Android/tdlib — explicitly not for external use
- tdlibx/td-ktx — archived 2024, dead
- Build it yourself — broken on macOS, 45min Docker build, CI setup hours

This project automates the entire thing. CI polls upstream every 6 hours, builds for all ABIs, and publishes to Maven Central on new TDLib versions. You get a PR to review with the API diff before publish. One merge. Done.

## Usage Guide for FOSS Developers

This library is designed to be plug-and-play for any open-source or commercial Telegram client on Android. Follow these guidelines to integrate TDLib into your project securely and professionally.

### 1. Repository & Dependency Configuration
Ensure `mavenCentral()` is defined in your repository list, then add the core prebuilt JNI library and the optional Kotlin Coroutines/Flow extension to your `build.gradle.kts` (app module):

```kotlin
// settings.gradle.kts
dependencyResolutionManagement {
    repositories {
        google()
        mavenCentral() // Core library is hosted here
    }
}

// app/build.gradle.kts
dependencies {
    // Precompiled TDLib native C++ library with all 4 ABIs (arm64-v8a, armeabi-v7a, x86_64, x86)
    implementation("io.github.tdlib-android:core:1.8.64")
    
    // Sleek Kotlin Coroutines + Flow wrapper (Highly Recommended for FOSS apps)
    implementation("io.github.tdlib-android:ktx:1.8.64")
}
```

### 2. Initializing TdClient Secures
In your application class or dependency injection graph, initialize the TDLib client wrapper. Pass your custom `apiId` and `apiHash` dynamically (avoid hardcoding them in your repository—use environment variables, `BuildConfig`, or Gradle properties):

```kotlin
import io.github.tdlibandroid.ktx.TdClient
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch

// 1. Manually load the prebuilt native JNI library
System.loadLibrary("tdjni")

// 2. Instantiate the client with your database path and Telegram API credentials
val filesDir = context.filesDir.absolutePath + "/tdlib"
val client = TdClient(
    filesDir = filesDir,
    verbosityLevel = 1, // 1 = Error/Fatal, 5 = Verbose Debugging
    apiId = BuildConfig.TELEGRAM_API_ID,   // Load securely from build config
    apiHash = BuildConfig.TELEGRAM_API_HASH // Load securely from build config
)

// 3. Initialize and collect updates
client.init()

CoroutineScope(Dispatchers.IO).launch {
    client.updates.collect { update ->
        // Listen to all incoming MTProto and Auth updates reactively!
    }
}
```

---

## Author & Credits 👑

This project was envisioned, architected, and is actively maintained by **[Akash Priyadarshi (@AkashPriyadarshii)](https://github.com/AkashPriyadarshii)**. 

Akash created this distribution to solve the massive friction of manually compiling TDLib from source for multiple Android architectures. Through custom Docker matrix builds and automated upstream watchdogs, this project provides the global Android open-source ecosystem with a zero-maintenance, up-to-date, and production-grade precompiled TDLib solution. 

If this library saves you time or powers your FOSS app, please consider starring the repository and crediting Akash in your project's credits page!

---

## Version History

Auto-generated from TDLib upstream. See [CHANGELOG.md](CHANGELOG.md).

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) — CI architecture, how to add ABI support, how to contribute to the ktx wrapper.

## License

- The TDLib C++ binary and generated Java interfaces are licensed under the **Boost Software License 1.0 (BSL-1.0)**.
- The `ktx` wrapper module is licensed under the **Apache License 2.0**.

