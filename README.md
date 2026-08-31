# tdlib-android

Precompiled [TDLib](https://github.com/tdlib/td) for Android — all 4 ABIs, built by CI, distributed as AARs via GitHub Releases.

No compiling TDLib from source. No `.so` wrangling. Works with any Telegram client, bot UI, or MTProto-based Android app.

> Status: **early / experimental.** The AARs are built and released, but this is not yet published to a package repository, so you install from GitHub Releases (below). Use at your own risk.

> **Website:** marketing site with a full setup guide at [akashpriyadarshii.github.io/tdlib-android](https://akashpriyadarshii.github.io/tdlib-android/).

## Install from GitHub Releases

Download from the [latest release](https://github.com/AkashPriyadarshii/tdlib-android/releases/latest):

- `core-release.aar` — prebuilt TDLib native library for all 4 ABIs (~39 MB)
- `ktx-release.aar` — Kotlin Coroutines/Flow wrapper (optional, ~44 KB)
- `checksums.txt` — SHA-256 checksums

Then put the AARs in a local module and depend on it. Example with a `libs/` directory in your project:

```kotlin
// settings.gradle.kts
dependencyResolutionManagement {
    repositories {
        google()
        mavenCentral()
        flatDir { dirs("libs") }
    }
}

// app/build.gradle.kts
dependencies {
    implementation(files("libs/core-release.aar"))  // Prebuilt TDLib — all 4 ABIs
    implementation(files("libs/ktx-release.aar"))   // Optional Kotlin Coroutines/Flow wrapper
}
```

## ABI Coverage

| ABI | Devices |
|---|---|
| `arm64-v8a` | All modern Android (2016+) |
| `armeabi-v7a` | 32-bit ARM devices |
| `x86_64` | Android emulators (recommended for CI) |
| `x86` | Legacy emulators |

**Tested on:** Realme GT 7 (Dimensity 9400e) · Android 16 (API 36)

## Why this exists

I built this project on a **Windows 11 machine with just 4GB of RAM**. Compiling TDLib locally with the Android NDK on low-end hardware is a nightmare: the C++ compiler runs out of memory, crashes halfway through, takes hours, and freezes the machine.

Every other option as of 2026:

- up9cloud/android-libtdjson — frozen at 1.8.52, GitHub token required, raw .so only
- TGX-Android/tdlib — explicitly not for external use
- tdlibx/td-ktx — archived 2024, dead
- Build it yourself — painful on low-RAM hardware

So the heavy lifting was shifted to the cloud: GitHub Actions compiles the native library for all 4 ABIs on high-memory runners, wraps them in AARs, and attaches them to a release. CI also polls upstream for new TDLib versions.

## Usage

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

Created and maintained by **[Akash Priyadarshi (@AkashPriyadarshii)](https://github.com/AkashPriyadarshii)** to eliminate the complexity of compiling TDLib from source for multiple Android architectures. Docker matrix builds and automated upstream workflows handle the compilation.

---

## Version History

Tracks TDLib upstream. See [CHANGELOG.md](CHANGELOG.md).

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) — CI architecture, ABI builds, and contributing guidelines.

## License

- TDLib binary and Java interfaces: **Boost Software License 1.0 (BSL-1.0)**.
- `ktx` wrapper module: **Apache License 2.0**.
