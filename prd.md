# tdlib-android — Product Requirements Document (PRD)

**Version:** 0.1.0  
**Status:** Approved / Production Specification  
**Target Release:** v0.1.0  
**Maintainer:** Akash Priyadarshi ([@AkashPriyadarshii](https://github.com/AkashPriyadarshii))  
**Organization:** `tdlib-android`  
**Maven Central Artifacts:** `io.github.tdlib-android:core:0.1.0` · `io.github.tdlib-android:ktx:0.1.0`  
**License:** BSL-1.0 (`:core`) / Apache-2.0 (`:ktx`)  

---

## 1. Executive Summary & Problem Statement

Telegram Database Library ([TDLib](https://github.com/tdlib/td)) is the official, complete cross-platform client library for building custom Telegram clients, bot frontends, and automated MTProto applications. However, using TDLib on Android is notoriously difficult:
- Compiling from C++ source requires 16+ GB RAM, a full NDK toolchain, CMake, OpenSSL, and 2+ hours of build time. Standard developer machines (and 4–6 GB RAM workstations) suffer out-of-memory crashes (`exit code 137`).
- Existing community distributions are either abandoned (`tdlibx/td-ktx`), frozen years behind (`up9cloud/android-libtdjson` frozen at 1.8.52 requiring GitHub token auth), private (`TGX-Android`), or functionally broken (`g000sha256/tdl-coroutines`).
- Modern Android 15+ devices require 16 KB memory page size alignment (`-Wl,-z,max-page-size=16384`), which older prebuilt binaries do not provide.

**`tdlib-android`** is a zero-cost, community-maintained, CI-automated distribution that delivers precompiled, 16 KB page-aligned TDLib AARs for all 4 Android architectures directly via Maven Central, accompanied by a reactive Kotlin Coroutines/Flow bridge.

---

## 2. Target Personas & Value Proposition

| Persona | Pain Point | Value Provided by `tdlib-android` |
| :--- | :--- | :--- |
| **Android FOSS Client Developers** | Compiling C++ TDLib stalls local dev and CI runners. | Drop-in `implementation("io.github.tdlib-android:core:0.1.0")` via Maven Central. Zero local NDK required. |
| **Telegram Infrastructure Builders** | Managing multi-ABI `.so` files and JNI glue manually. | Prebuilt AAR packaging all 4 ABIs with auto-generated `TdApi.java` and bundled ProGuard consumer rules. |
| **Kotlin/Compose Engineers** | TDLib's raw native callback loop is cumbersome in reactive UIs. | Light reactive `:ktx` wrapper exposing `suspend fun send()` and `val updates: Flow<TdApi.Update>`. |
| **Constrained CI Pipelines** | Runner timeout and RAM exhaustion during native builds. | All native compilation is offloaded to automated upstream GitHub Actions pipelines. |

---

## 3. Product Scope

### 3.1 In-Scope (v0.1.0)

1. **`:core` Module (AAR Distribution):**
   - Embedded `libtdjson.so` for all 4 production ABIs: `arm64-v8a`, `armeabi-v7a`, `x86_64`, `x86`.
   - Android 15 forward-compatibility: compiled with NDK r27c (`27.2.12479018`) with `-Wl,-z,max-page-size=16384`.
   - Auto-generated Java JNI bindings: `TdApi.java` and `Client.java`.
   - Shipped `consumer-rules.pro` preventing R8/ProGuard from stripping native JNI symbols.
   - Maven Central publication under `io.github.tdlib-android:core`.

2. **`:ktx` Module (Coroutines/Flow Bridge):**
   - ~150-line thin, non-opinionated Kotlin coroutines wrapper (`TdClient`).
   - `suspend fun <T : TdApi.Object> send(function: TdApi.Function<T>): T`.
   - Reactive event stream: `val updates: Flow<TdApi.Update>`.
   - Lifecycle management: `init()`, `close()`, and `awaitReady()`.
   - Maven Central publication under `io.github.tdlib-android:ktx`.

3. **`:sample` Module:**
   - Minimal runnable Android sample validating initialization, authentication state observation, and chat listing.

4. **Automated CI/CD Engine:**
   - Upstream version watchdog polling `tdlib/td` every 6 hours.
   - Parallel 4-ABI Docker matrix builds with 10 GB swap space to prevent runner OOM.
   - Strict binary gate: `scripts/verify-abi-count.sh` validating ELF headers via `readelf -h`.
   - Auto-generated PR with diff and SHA-256 checksums for human maintainer review.
   - Automated Maven Central deployment + GitHub Release upon PR merge.
   - Post-deployment smoke test verifying dependency resolution and binary loading.

### 3.2 Out-of-Scope (Deferred to v0.2+)

- Kotlin Multiplatform (KMP) iOS / macOS / Desktop targets.
- High-level opinionated auth DSL (phone number formatters, OTP countdown UI).
- Prebuilt Jetpack Compose UI component libraries.
- Application-layer database sync or offline caching abstraction.
- Telegram HTTP Bot API wrapping (use standard REST clients like Ktor/Retrofit instead).

---

## 4. System Architecture & Component Design

```
+-------------------------------------------------------------+
|                     Android Application                     |
|          (Jetpack Compose / XML / Modern Coroutines)        |
+-------------------------------------------------------------+
                               |
                               v
+-------------------------------------------------------------+
|               io.github.tdlib-android:ktx                   |
|   - TdClient (Lifecycle, CoroutineScope, Dispatchers.IO)    |
|   - suspend fun send(Function<T>): T                        |
|   - val updates: Flow<TdApi.Update> (SharedFlow buffer)     |
+-------------------------------------------------------------+
                               |
                               v
+-------------------------------------------------------------+
|               io.github.tdlib-android:core                  |
|   - Java JNI Glue (Client.java, TdApi.java)                 |
|   - Prebuilt libtdjson.so (4 ABIs: arm64, armv7, x86, x64)  |
|   - consumer-rules.pro (-keep class org.drinkless.tdlib.**) |
+-------------------------------------------------------------+
                               |
                               v
+-------------------------------------------------------------+
|              Telegram MTProto Gateway Servers               |
+-------------------------------------------------------------+
```

### 4.1 Module Specifications

#### Module 1: `:core`
- **Output:** `core-release.aar`
- **Minimum SDK:** 26 (Android 8.0 Oreo)
- **Target SDK:** 35 (Android 15)
- **Native Architectures:**
  - `arm64-v8a` (Primary modern 64-bit mobile devices)
  - `armeabi-v7a` (Legacy 32-bit mobile devices)
  - `x86_64` (Modern 64-bit Android Studio emulators)
  - `x86` (Legacy 32-bit Android Studio emulators)
- **ProGuard / R8 Consumer Rules (`core/consumer-rules.pro`):**
  ```proguard
  -keep class org.drinkless.tdlib.** { *; }
  -keepclassmembers class org.drinkless.tdlib.** { *; }
  -dontwarn org.drinkless.tdlib.**
  ```

#### Module 2: `:ktx`
- **Dependencies:** `:core`, `org.jetbrains.kotlinx:kotlinx-coroutines-core:1.8.1`
- **Core API (`TdClient.kt`):**
  - Thread-safe initialization and lifecycle cleanup.
  - Non-blocking asynchronous request handling via Kotlin `suspendCancellableCoroutine`.
  - Non-blocking broadcast of incoming MTProto updates via Kotlin coroutine `SharedFlow`.

---

## 5. CI/CD & Automation Specifications

```
┌─────────────────────────────────────────────────────────────┐
│                   AUTOMATED PIPELINE                         │
│                                                             │
│  [Cron: every 6h]                                           │
│  check-upstream.yml                                         │
│    │                                                         │
│    ▼                                                         │
│  Poll tdlib/td CMakeLists.txt VERSION field via GitHub API  │
│  Compare with local VERSION file                             │
│    │                                                         │
│    ├── MATCH → Exit 0 (no-op)                                │
│    │                                                         │
│    └── DIFF → Trigger build.yml                              │
│                  │                                           │
│                  ▼                                           │
│         Parallel Build Matrix (4 ABIs):                      │
│         - arm64-v8a  - armeabi-v7a                          │
│         - x86_64     - x86                                  │
│                  │                                           │
│                  ▼                                           │
│         Docker Build with Swap Space (10GB)                  │
│         Compile libtdjson.so + generate TdApi.java           │
│                  │                                           │
│                  ▼                                           │
│         Merge & Verification:                                │
│         - scripts/verify-abi-count.sh (readelf -h)           │
│         - Gradle assembleRelease → .aar                      │
│         - Smoke test: load .aar & call getOption("version")  │
│                  │                                           │
│                  ▼                                           │
│  ⚠️ HUMAN GATE: Auto-opened PR with diff & SHA-256           │
│     Maintainer reviews API diff and merges                  │
│                  │                                           │
│                  ▼                                           │
│  publish.yml (on merge):                                     │
│  - GPG Sign artifacts                                        │
│  - Publish to Sonatype Central Portal (Maven Central)        │
│  - Create GitHub Release with checksums                      │
│                  │                                           │
│                  ▼                                           │
│  smoke-test-publish.yml (10m post-publish):                  │
│  - Resolves artifacts from Maven Central                     │
│  - Builds test harness and asserts clean execution           │
└─────────────────────────────────────────────────────────────┘
```

### 5.1 Workflows
1. **`check-upstream.yml`:** Polls `CMakeLists.txt` and `td_api.tl` schema commit hash every 6 hours via GitHub REST API.
2. **`build.yml`:**
   - Multi-arch Docker build using pinned Android NDK `27.2.12479018`.
   - Injects `pierotofy/set-swap-space@master` (10 GB swap) ensuring 17 GB total virtual memory.
   - Enforces `fail-fast: true` across matrix jobs.
3. **`publish.yml`:** Runs `com.vanniktech.maven.publish` with in-memory GPG signing on PR merge.
4. **`smoke-test-publish.yml`:** End-to-end pull and test from Maven Central after 10-minute CDN propagation window.

---

## 6. Error Matrix & Resiliency Standards

| Failure Mode | Detection Gate | Automated Remediation / Policy |
| :--- | :--- | :--- |
| **Docker Build OOM (Exit 137)** | Docker exit code 137 | Runner adds 10 GB swap pre-build. Total available RAM: 17 GB. |
| **Single ABI Build Failure** | Matrix job exit code ≠ 0 | `fail-fast: true` aborts release immediately. Never ship partial ABI set. Opens GitHub Issue. |
| **Incomplete `TdApi.java`** | File size check < 100 KB | Build fails immediately. Releases aborted. |
| **Missing ABI in AAR** | `scripts/verify-abi-count.sh` | Uses `readelf -h` to verify ELF architecture headers. Aborts if count ≠ 4. |
| **Sonatype Publish Timeout** | HTTP timeout (300s) | Exponential backoff retry (10s, 20s, 40s, 80s, 160s). Staging preserved. |
| **Sonatype 401 (Expired Creds)** | HTTP 401 response | Immediate GitHub Issue opened tagged `credentials-expired`. No blind retries. |
| **KTX Wrapper Compile Error** | `compileReleaseKotlin` exit code | PR creation blocked. Issue opened tagged `breaking-api-change` with compiler log. |
| **Published AAR Runtime Failure** | `smoke-test-publish.yml` | Opens high-priority Issue `PUBLISH BROKEN`, flags release for immediate deprecation. |

---

## 7. Non-Functional Requirements (NFRs)

- **₹0 Budget Constraint:** Entire pipeline operates within GitHub Actions free tier (unlimited for public repositories) and Sonatype Central OSS tier.
- **Zero Local Hardware Requirement:** No local compilation on 4–6 GB RAM developer laptops. All binaries built in the cloud.
- **ELF Validation Gate:** Never rely on file size; every architecture must match standard ELF headers (`AArch64`, `ARM`, `Advanced Micro Devices X86-64`, `Intel 80386`).
- **Binary Page Alignment:** Strict 16 KB page alignment (`-Wl,-z,max-page-size=16384`) across all ABIs for Google Play compliance.
- **Security & Secret Hygiene:** GPG private keys and Sonatype tokens strictly injected via GitHub Secrets. Pre-push and pre-release audits via `gitleaks` and `foxguard`.
- **Zero Telemetry Guarantee:** Prebuilt binaries contain zero tracking, advertising, analytics, or third-party proxy layers. All traffic routes direct to Telegram MTProto data centers.

---

## 8. Definition of Done (v0.1.0 Gate)

- [x] Multi-module Gradle configuration (`:core`, `:ktx`, `:sample`) operational.
- [x] Docker build configuration compiling pinned NDK r27c for all 4 ABIs with 16 KB page size support.
- [x] `scripts/verify-abi-count.sh` verifying all 4 ABIs using `readelf -h`.
- [x] `consumer-rules.pro` properly packaged into `:core` AAR bundle.
- [x] `TdClient.kt` unit tested with 80%+ test coverage.
- [x] `check-upstream.yml`, `build.yml`, `publish.yml`, and `smoke-test-publish.yml` configured and verified.
- [x] Sample app builds cleanly against `:core` and `:ktx` modules.
- [x] Sonatype Central Portal coordinates and GPG in-memory signing verified.
- [x] Public documentation (`docs/`, `README.md`, `llms.txt`) deployed and verified.
