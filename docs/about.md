# About tdlib-android

> Precompiled TDLib AARs for Android across all 4 ABIs (arm64-v8a, armeabi-v7a, x86_64, x86) with zero local NDK compilation and a reactive Kotlin Coroutines/Flow wrapper.

## Mission & Background

Compiling the Telegram Database Library (TDLib) from C++ source is notoriously difficult. It requires the complete Android NDK toolchain, CMake, OpenSSL, zlib, and at least 16 GB of RAM. On constrained developer machines, compiling TDLib takes hours, triggers out-of-memory crashes, and risks version drift.

tdlib-android was conceived on a Windows 11 machine with only 4 GB of RAM — where local TDLib compilation is impossible. The project solves this through automated cloud engineering:
- Automated version watchdog checks TDLib master every 6 hours.
- Parallel Docker matrix builds compile and package all 4 native architectures.
- Rigorous CI verification gates inspect ELF headers using `readelf -h` to guarantee 100% ABI completeness.
- Verified artifacts are signed and published directly to Maven Central and GitHub Releases.

## Architectural Highlights

- **All 4 ABIs:** Ships `arm64-v8a`, `armeabi-v7a`, `x86_64`, and `x86`.
- **Android 15+ 16 KB Page Support:** Built using NDK r27c with `-Wl,-z,max-page-size=16384`.
- **Zero Third-Party Native Dependencies:** Only TDLib upstream and Android libc/libm.
- **Kotlin Wrapper:** 150-line reactive bridge (`io.github.tdlib-android:ktx`) exposing `suspend fun send()` and `val updates: Flow<TdApi.Update>`.

## Maintainer Profile

- **Maintainer:** Akash Priyadarshi
- **Location:** Patna, Bihar, India
- **Profile:** Self-taught systems and Android engineer focused on Binder IPC, Android ART internals, Rust systems tooling, and autonomous AI coding agent architectures.
- **Portfolio:** https://akashpriyadarshi.vercel.app
- **GitHub:** https://github.com/AkashPriyadarshii
- **LinkedIn:** https://linkedin.com/in/akash-priyadarshi-1aa51b37a
- **Resume:** https://akashpriyadarshii.github.io/Resume/

## Licensing

- Core TDLib Engine: Boost Software License 1.0 (BSL-1.0)
- Kotlin Coroutines Wrapper: Apache License 2.0
- Available freely via Maven Central: `io.github.tdlib-android:core` and `io.github.tdlib-android:ktx`.
