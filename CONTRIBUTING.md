# Contributing to tdlib-android

Thank you for contributing! This project is a fully automated distribution pipeline designed to keep TDLib prebuilt AAR libraries for Android up-to-date and easily installable via Maven Central.

## CI/CD Pipeline Architecture

```
upstream version change → check-upstream.yml detects → build.yml runs matrix →
PR opened with diff + checksums → Akash reviews → merge → publish.yml publishes →
smoke-test-publish.yml verifies on Maven Central
```

1.  **Upstream Watchdog (`check-upstream.yml`)**: Chronologically polls tdlib/td repo version parameters and scheme changes via GitHub API every 6 hours.
2.  **Multitarget Compiler (`build.yml`)**: Spawns a parallel build matrix for all 4 required ABIs inside official Docker environments on Ubuntu Actions runners. Pinned NDK `27.2.12479018` is enforced.
3.  **Binary Head checks (`verify-abi-count.sh`)**: Direct ELF verification via `readelf -h` to secure binary headers instead of fragile file size comparisons.
4.  **Verification Compile (`smoke-test.sh`)**: Creates temporary Android apps compiling directly against core and ktx modules locally before publishing.

## Local Development & Builds

Although all heavy compilations (C++ Docker builds) run strictly on GitHub runners to prevent local system freezes, you can build and run tests for Java and Kotlin modules locally:

```bash
# Verify configurations and modular task lists
./gradlew help

# Assemble Kotlin Coroutine and sample wrappers
./gradlew assemble
```

## Absolute Constraints (Never Bypass)
*   **4 ABIs always**: `arm64-v8a`, `armeabi-v7a`, `x86_64`, `x86`. Never exclude or reduce.
*   **Never commit `.so` or `TdApi.java`**: Keep these binary/giant generated artifacts strictly gitignored.
*   **Fail-fast matrix**: A compilation drop in any ABI blocks the entire release immediately.
*   **Security scans**: Stage checks (`gitleaks`) must pass before commits.
