# tdlib-android

> Precompiled TDLib (Telegram Database Library) AARs for Android. All 4 ABIs (`arm64-v8a`, `armeabi-v7a`, `x86_64`, `x86`), CI-built, zero local NDK compilation required, with Kotlin Coroutines/Flow wrapper.

- **Current Version:** 0.1.0 (packaging TDLib 1.8.x)
- **Minimum SDK:** API 26 (Android 8.0 Oreo)
- **Target SDK:** API 35 (Android 15 forward-compatible with 16 KB page size support)
- **Core AAR:** `io.github.tdlib-android:core:0.1.0` (BSL-1.0)
- **Kotlin Wrapper:** `io.github.tdlib-android:ktx:0.1.0` (Apache-2.0)
- **Canonical Site:** https://tdlib-android.vercel.app/

---

## Why this exists

Compiling TDLib locally requires 16+ GB RAM, a full NDK toolchain, and hours of build time that easily causes OOM crashes on standard developer machines. tdlib-android offloads compilation to automated GitHub Actions CI pipelines:
- Watchdog cron polls TDLib upstream master every 6 hours.
- Docker matrix compiles all 4 native architectures with pinned NDK r27c.
- Binary verification gates validate ELF headers using `readelf -h`.
- Automated PR with full diff and checksums opens for human review.
- Merging publishes signed AARs directly to Maven Central.

---

## Quick Setup

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
    implementation("io.github.tdlib-android:core:0.1.0")
    implementation("io.github.tdlib-android:ktx:0.1.0")
}
```

---

## Basic Usage

```kotlin
// 1. Load native JNI library
System.loadLibrary("tdjson")

// 2. Initialize TdClient with dedicated app storage directory
val client = TdClient(filesDir = context.filesDir.absolutePath + "/tdlib")
client.init()

// 3. React to updates via Kotlin Coroutines Flow
CoroutineScope(Dispatchers.IO).launch {
    client.updates.collect { update ->
        when (update) {
            is TdApi.UpdateAuthorizationState -> {
                // handle authorization state
            }
            is TdApi.UpdateNewMessage -> {
                // handle incoming message
            }
        }
    }
}
```

---

## When to Use This

- Building custom Telegram Android clients or automated messaging agents.
- Projects without local NDK compilation setup or on low-RAM developer hardware.
- Apps requiring all 4 ABIs and forward-compatibility with 16 KB memory page sizes on Android 15+.
- Reactive Kotlin architectures utilizing `Flow<TdApi.Update>`.

For detailed agent integration guidance, see [Agent Instructions](https://tdlib-android.vercel.app/agent-instructions.md).

---

## Documentation & Machine-Readable Endpoints

- [Setup Guide](https://tdlib-android.vercel.app/setup): 3-step Gradle configuration, ProGuard rules, and API setup.
- [Agent Instructions](https://tdlib-android.vercel.app/agent-instructions.md): When-to-use and agent implementation instructions.
- [About & Maintainer](https://tdlib-android.vercel.app/about): Background, architecture, and maintainer details.
- [Contact & Support](https://tdlib-android.vercel.app/contact): Bug reports and security disclosures.
- [Privacy Policy](https://tdlib-android.vercel.app/privacy): Zero-telemetry guarantees.
- [XML Sitemap](https://tdlib-android.vercel.app/sitemap.xml): Machine-readable site index.
- [LLM Index (llms.txt)](https://tdlib-android.vercel.app/llms.txt): Token-efficient AI agent context.
- [GitHub Releases](https://github.com/AkashPriyadarshii/tdlib-android/releases): Download signed AARs and checksums.
- [Maven Central Core](https://central.sonatype.com/artifact/io.github.tdlib-android/core): Sonatype package details.
