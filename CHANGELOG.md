# Changelog

All notable changes to this project will be documented in this file.

This project is an automated TDLib distribution that tracks the upstream repository [tdlib/td](https://github.com/tdlib/td).

## [1.8.64] - May 2026

### Added
- Initial release of community-maintained prebuilt TDLib Android AAR distribution.
- Automated upstream watchdog monitoring version and schema transitions.
- Multi-ABI matrix builds compiling `arm64-v8a`, `armeabi-v7a`, `x86_64`, and `x86`.
- Proguard keep rules (`consumer-rules.pro`) packaged directly into the AAR.
- Thin Kotlin Coroutines wrapper supporting suspendable dispatches and updates flow.
