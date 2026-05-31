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

## Used by
- [OurDrive](https://github.com/AkashPriyadarshii/OurDrive) — private encrypted Android cloud storage

[Open a PR to add your project]

## Version History

Auto-generated from TDLib upstream. See [CHANGELOG.md](CHANGELOG.md).

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) — CI architecture, how to add ABI support, how to contribute to the ktx wrapper.

## License

TDLib and its Java interface are licensed under [BSL-1.0](https://www.boost.org/LICENSE_1_0.txt).
This wrapper (ktx module) is Apache 2.0.
