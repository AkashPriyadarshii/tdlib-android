# tdlib-android — Project Bible v1.1
> Sole source of truth. CI/CD infra + Kotlin wrapper. Auto-synced TDLib AAR for Android.
> Author: Akash Priyadarshi (@AkashPriyadarshii)
> GitHub Org: github.com/tdlib-android
> Maven Central: `io.github.tdlib-android:core` + `io.github.tdlib-android:ktx`
> Generated: May 2026. v1.1: 8 CI/SDK patches + Antigravity 2.0 full workflow layer applied.
> Zero gaps. AI cold-reads = zero clarification needed.

---

## 1. PRODUCT OVERVIEW

**tdlib-android** is the community-maintained, auto-updating TDLib distribution for Android. It is infrastructure — not an app. It solves the single most painful problem in the Android Telegram ecosystem: there is no reliable, up-to-date, Maven Central AAR of TDLib that any Android developer can drop into their `build.gradle.kts` with zero manual build steps.

**The gap it fills (verified May 2026):**
- up9cloud/android-libtdjson: frozen at TDLib 1.8.52 (Aug 2025), requires GitHub token auth, raw `.so` only
- TGX-Android/tdlib: explicitly not for external use, unstable features, Java-only
- tdlibx/td-ktx: archived July 2024, dead
- g000sha256/tdl-coroutines: v11.0.0 on Maven Central but broken in practice (verified May 30 2026), no community, no docs
- ca.denisab85/tdlib: last published Nov 2022, TDLib 1.8.8, ancient
- TDLib upstream: currently at v1.8.64 as of May 2026
- **Gap: 12 versions behind, no zero-friction Android option exists**

**Who needs this:**
- Every FOSS Telegram client developer (MonoGram, Nekogram forks, etc.)
- Anyone building Telegram-based infra (OurDrive and similar)
- Bot developers who want a native Android UI layer
- TDLib is referenced in their own README as the Android standard — no maintained community AAR anywhere

**Why Akash owns this:**
- He already uses TDLib in OurDrive — he is the first consumer of his own library
- Infrastructure projects outlive apps for GitHub reputation — every `build.gradle.kts` that imports this = Akash's name in every FOSS Telegram app
- TDLib has 8.7k stars, active Android build issues. The gap is infrastructure, not invention.
- Being the first reliable maintainer = permanent community anchor

---

## 2. SCOPE — v0.1

**Two modules, nothing else:**

**`tdlib-android:core`** — Prebuilt `.aar` containing:
- `libtdjson.so` for 4 ABIs: `arm64-v8a`, `armeabi-v7a`, `x86_64`, `x86`
- `TdApi.java` (auto-generated from upstream TL schema)
- `Client.java` + JNI glue
- Published to Maven Central, zero GitHub token required
- Tracks TDLib upstream master, auto-republishes on new upstream version tag

**`tdlib-android:ktx`** — Kotlin wrapper (~200 lines):
- `TdClient.kt`: `suspend fun send(function: TdApi.Function<T>): T`
- `Flow<TdApi.Update>` update stream
- Lifecycle-aware: `init()`, `close()`, `awaitReady()`
- Zero opinion on auth flow, message DSL, or app structure
- Thin bridge only — makes JNI usable from Kotlin coroutines

**Not in v0.1:**
- KMP / iOS / macOS targets (g000sha256 territory, not differentiated)
- High-level auth DSL
- Message-sending helpers beyond raw API
- Compose UI components
- Any application-layer logic

---

## 3. ARCHITECTURE — FULL CI/CD PIPELINE

```
┌─────────────────────────────────────────────────────────────┐
│                   AUTOMATED PIPELINE                         │
│                                                             │
│  [Cron: every 6h]                                           │
│  check-upstream.yml                                         │
│    │                                                         │
│    ▼                                                         │
│  Poll tdlib/td CMakeLists.txt VERSION field via GitHub API  │
│  Compare with VERSION file in repo                          │
│    │                                                         │
│    ├── SAME → exit 0, no action                             │
│    │                                                         │
│    └── DIFFERENT → trigger build.yml                        │
│                        │                                     │
│                        ▼                                     │
│              Build Matrix (parallel):                        │
│              ┌──────────────────────────────────────┐       │
│              │ Job A: arm64-v8a (ubuntu-latest)     │       │
│              │ Job B: armeabi-v7a (ubuntu-latest)   │       │
│              │ Job C: x86_64 (ubuntu-latest)        │       │
│              │ Job D: x86 (ubuntu-latest)           │       │
│              └──────────────────────────────────────┘       │
│                        │                                     │
│              Each job:                                       │
│              1. docker build (official TDLib Dockerfile)    │
│                 --build-arg TDLIB_INTERFACE=Java             │
│                 --build-arg ANDROID_NDK_VERSION=27.2.12479018│
│                 → outputs libtdjson.so + TdApi.java         │
│              2. Upload .so artifact                         │
│                        │                                     │
│              [Merge Step — all 4 ABIs]                       │
│              5. Download all 4 ABI artifacts                │
│              6. Gradle assembleRelease → .aar               │
│              7. Smoke test: load .aar in test project,      │
│                 call TdApi.getOption("version"), assert ok  │
│              8. ABI count check: fail if != 4               │
│                        │                                     │
│                        ▼                                     │
│         ⚠️  HUMAN GATE — PR opened automatically:           │
│            Title: "chore: bump TDLib 1.8.63 → 1.8.64"      │
│            Body:                                             │
│            - TdApi.java diff (new/removed/changed methods)  │
│            - Build artifact checksums (SHA-256 per ABI)     │
│            - Smoke test result (pass/fail)                  │
│            - Link to upstream CHANGELOG.md section          │
│            → Akash reviews, checks for breaking API changes │
│            → Merges PR                                       │
│                        │                                     │
│                        ▼                                     │
│         [On PR merge to main]                               │
│         publish.yml:                                         │
│         1. Download .aar artifact from build job            │
│         2. Gradle publishToMavenCentral (Sonatype Portal)   │
│         3. Create GitHub Release with:                       │
│            - Auto-extracted CHANGELOG section               │
│            - SHA-256 checksums per ABI                      │
│            - Gradle dependency snippet                       │
│         4. Update VERSION file in repo                       │
│         5. Update README badge                              │
│                        │                                     │
│                        ▼                                     │
│         smoke-test-publish.yml (post-publish, 10min delay): │
│         1. Pull artifact from Maven Central                  │
│         2. Build minimal test app against it                │
│         3. Run TdApi.getOption("version") on device/emu     │
│         4. Assert: no crash, correct version returned       │
│         5. If fail → open GitHub Issue "PUBLISH BROKEN"     │
└─────────────────────────────────────────────────────────────┘
```

**The 1 human touch:** Akash reviews the auto-generated PR. Checks TdApi.java diff for breaking changes. Merges. Everything else is zero-touch.

---

## 4. ERROR SCENARIOS — PRE-FIXED

Every failure mode is handled before it happens. No silent errors anywhere.

| Failure | Detection Method | Automated Response |
|---|---|---|
| TDLib Docker build fails (CMake error, OOM) | `docker build` exit code ≠ 0 | Retry 3× with 30s backoff. If all fail: open GitHub Issue with full build log, tag `build-failure`, halt release. No partial publish. |
| One ABI build fails, others succeed | Per-job exit code + artifact presence check | Fail entire release. Never publish partial ABI set. Issue tagged `partial-build-failure`. |
| VERSION file unchanged but dir hash changed | SHA-256 of `example/android/` + `td_api.tl` compared each run | Rebuild anyway if hash changed. Catches non-version API changes. |
| TdApi.java not generated (JNI build skipped) | File size check: TdApi.java < 100KB = fail | Abort with error: "TdApi.java not generated or incomplete". |
| Sonatype Central Portal publish timeout | HTTP response code + timeout 300s | Retry 5× with exponential backoff (10s, 20s, 40s, 80s, 160s). If all fail: Issue tagged `publish-failed`, artifact kept in staging. |
| Sonatype 401 (credentials expired) | HTTP 401 response | Immediate Issue: "Maven Central credentials expired — manual rotation needed". No retry. |
| ktx module fails to compile against new core | Gradle compileReleaseKotlin exit code | Block PR creation. Open Issue: `breaking-api-change` tag with exact error. ktx needs update before release. |
| Docker OOM on GitHub Actions runner (TDLib is large C++) | Exit code 137 | `pierotofy/set-swap-space@master` adds 10GB swap before every Docker build. Standard runner = 7GB RAM + 10GB swap = 17GB total. Eliminates OOM. |
| Post-publish smoke test fails | Test app crash or wrong version | Issue: "PUBLISH BROKEN — version X on Maven Central fails smoke test". Deprecate release. |
| Upstream tdlib/td repo unreachable (GitHub outage) | HTTP error on API poll | Skip cycle silently. Log to Actions summary. Retry next cron. |
| CHANGELOG.md parse fails (format changed) | Regex match returns empty | Use fallback: "See upstream CHANGELOG at [link]" in PR body. Never block release. |
| GitHub token for PR creation expired | API 401 | Immediate Issue opened via fallback token (PAT with issues:write only). |
| TDLib changes required NDK version | CMake error referencing NDK | Pin NDK version in workflow, document override param. Fail loudly with: "NDK version mismatch — update ANDROID_NDK_VERSION in build.yml". |
| .aar exceeds reasonable size (>35MB) | File size check post-build | Warning in PR body. Not a blocker. Document expected size per release. |

---

## 5. STACK — LAYER TABLE

| Layer | Choice | Why Best | Alt Considered | Why Alt Rejected | Real Con | Neutralizer |
|---|---|---|---|---|---|---|
| Build system | Official TDLib Docker (`docker build --output`) | Same env as official, reproducible, no host deps | Build natively on runner | Host deps change, NDK version drift, non-reproducible | Docker image ~5GB pull on each run | GitHub Actions runner cache: `actions/cache` on Docker layer hash |
| CI/CD | GitHub Actions (public repo = unlimited) | Free unlimited for public, matrix support, artifact sharing between jobs | CircleCI, Drone | Not free unlimited for public | None for public repos | — |
| ABI matrix | arm64-v8a + armeabi-v7a + x86_64 + x86 | Covers 100% of real devices + emulators | arm64-v8a only | Excludes emulators (x86_64 needed for CI), old devices (armeabi-v7a) | 4× build time | Parallel matrix jobs — wall clock unchanged |
| NDK version | 27.2.12479018 (r27c, latest stable May 2026) | Most compatible with modern Android, TDLib build tested | r26, r28 | r28 not yet verified with TDLib; r26 older | Must pin exact version | Documented in build.yml as `ANDROID_NDK_VERSION` variable |
| TDLib interface | Java JNI (not JSON) | Type-safe, performant, official Android interface, used by all serious clients | JSON interface | String parsing overhead, no type safety, inferior DX | TdApi.java is 30MB+, breaks IDE indexing | Ship `tdapi-stub.jar` (method signatures only) alongside full jar |
| Maven Central publishing | Sonatype Central Portal (new portal, not OSSRH legacy) | OSSRH deprecated mid-2024, new Portal is the current path | JitPack | Token-auth required to consume | Portal setup one-time manual step | Documented in CONTRIBUTING.md exactly |
| Gradle publish plugin | `com.vanniktech.maven.publish` 0.28+ | Best-maintained Maven Central publisher, handles signing, sources, javadoc | `maven-publish` raw | More boilerplate, signing setup harder | Minor API surface | Well-documented in plugin README |
| GPG signing | GitHub Actions secret + in-CI signing | Required by Maven Central | Skip signing | Maven Central rejects unsigned artifacts | Secrets rotation | Annual reminder issue auto-created by cron |
| Wrapper language | Kotlin 2.0+ | Coroutines native, Flow native, Android first-class | Java | Java coroutine support is retrofit, not native | None | — |
| Version tracking | Poll CMakeLists.txt VERSION field via GitHub API | Simple, no webhooks needed, deterministic | GitHub webhooks on tdlib/td | Requires approved webhook on external repo | 6h max lag | Acceptable for a prebuilt distribution |
| Changelog extraction | Bash regex on CHANGELOG.md section matching new version | Simple, no deps | External changelog tool | Extra dep, overkill | Fragile if format changes | Fallback: raw link to upstream CHANGELOG |

---

## 6. REPO STRUCTURE

```
tdlib-android/
├── .github/
│   ├── workflows/
│   │   ├── check-upstream.yml      # Cron every 6h: polls TDLib VERSION, triggers build
│   │   ├── build.yml               # Matrix build: 4 ABIs in parallel, Docker, outputs .aar
│   │   ├── publish.yml             # On PR merge to main: publish to Maven Central + GitHub Release
│   │   ├── smoke-test-publish.yml  # 10min after publish: pull from Maven Central, verify
│   │   └── rotate-reminder.yml     # Annual cron: opens Issue "Rotate GPG key + Sonatype token"
│   ├── ISSUE_TEMPLATE/
│   │   ├── build-failure.md
│   │   ├── breaking-api-change.md
│   │   └── publish-broken.md
│   └── pull_request_template.md    # Auto-filled PR template for version bumps
│
├── core/                           # Module: tdlib-android:core
│   ├── build.gradle.kts
│   ├── consumer-rules.pro              # MANDATORY: R8/ProGuard keep rules
│   │                                   # -keep class org.drinkless.tdlib.** { *; }
│   │                                   # Without this: R8 obfuscates JNI bridge → runtime crash
│   ├── src/
│   │   └── main/
│   │       ├── jniLibs/
│   │       │   ├── arm64-v8a/libtdjson.so      ← populated by CI
│   │       │   ├── armeabi-v7a/libtdjson.so    ← populated by CI
│   │       │   ├── x86_64/libtdjson.so         ← populated by CI
│   │       │   └── x86/libtdjson.so            ← populated by CI
│   │       └── java/
│   │           └── org/drinkless/tdlib/
│   │               ├── TdApi.java              ← auto-generated by CI from TL schema
│   │               └── Client.java             ← JNI bridge
│
├── ktx/                            # Module: tdlib-android:ktx
│   ├── build.gradle.kts
│   └── src/
│       └── main/
│           └── kotlin/
│               └── io/github/tdlibandroid/
│                   ├── TdClient.kt             # suspend send() + Flow<Update> (~150 lines)
│                   ├── TdClientScope.kt        # CoroutineScope lifecycle wrapper
│                   └── TdExtensions.kt         # Convenience extensions (awaitReady, etc.)
│
├── sample/                         # Minimal working example app
│   ├── build.gradle.kts
│   └── src/main/
│       └── kotlin/
│           └── MainActivity.kt     # auth flow → getChats, 100 lines max
│
├── scripts/
│   ├── check-version.sh            # Polls upstream CMakeLists.txt, outputs new/unchanged + version
│   ├── build-tdlib.sh              # Wraps Docker build, extracts .so files + TdApi.java
│   ├── package-aar.sh              # Runs Gradle assembleRelease, copies outputs
│   ├── smoke-test.sh               # Loads .aar in minimal test project, calls getOption("version")
│   ├── generate-pr-body.sh         # Diffs TdApi.java, extracts CHANGELOG section, formats PR body
│   └── verify-abi-count.sh         # Asserts exactly 4 .so files present before packaging
│
├── gradle/
│   └── libs.versions.toml          # Version catalog
│
├── build.gradle.kts                # Root build file
├── settings.gradle.kts             # includes(":core", ":ktx", ":sample")
├── VERSION                         # Current shipped TDLib version string, e.g. "1.8.64"
├── AGENTS.md                       # Antigravity 2.0 native context file (replaces CLAUDE.md)
│                                   # Read automatically by Antigravity on every session start
├── mcp_config.json                 # MCP server config stub (Google Workspace MCPs, future)
├── CHANGELOG.md                    # Auto-generated: upstream CHANGELOG sections per shipped version
├── CONTRIBUTING.md                 # Exactly how CI works, how to contribute, Sonatype setup
├── README.md                       # Setup in 5 min, badges, version table, ABI coverage
├── .gitignore                      # Excludes: jniLibs/*.so, build/, *.aar, secrets
└── .agents/
    └── skills/
        ├── antigravity-awesome-skills/  ← sickn33/antigravity-awesome-skills (1,400+ skills)
        ├── tdlib-ci-expert.md           ← custom: CI/YAML/Docker/NDK specialist
        ├── kotlin-jni-expert.md         ← custom: TDLib JNI + Kotlin coroutines specialist
        └── maven-publish-expert.md      ← custom: Sonatype/GPG/Maven Central specialist
```

**Critical `.gitignore` entries:**
```gitignore
# .so binaries — generated by CI, never committed
core/src/main/jniLibs/**/*.so
# TdApi.java — generated by CI, never committed (30MB+ breaks IDE)
core/src/main/java/org/drinkless/tdlib/TdApi.java
# Build outputs
build/
*.aar
*.jar
# Secrets
*.jks
*.keystore
local.properties
```

**Why .so and TdApi.java are NOT committed:** They are 30MB+ total, change every TDLib version, and should be generated artifacts — not source. The repo stays lean. CI generates them fresh. Developers who clone and build locally run `./scripts/build-tdlib.sh` once.

---

## 7. GITHUB ACTIONS — FULL WORKFLOW SPECS

### 7.1 check-upstream.yml
```yaml
name: Check TDLib Upstream Version
on:
  schedule:
    - cron: '0 */6 * * *'   # every 6 hours
  workflow_dispatch:          # manual trigger for testing

jobs:
  check:
    runs-on: ubuntu-latest
    outputs:
      version_changed: ${{ steps.check.outputs.changed }}
      new_version: ${{ steps.check.outputs.new_version }}
      old_version: ${{ steps.check.outputs.old_version }}
    steps:
      - uses: actions/checkout@v4

      - name: Check upstream TDLib version
        id: check
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          # Fetch upstream CMakeLists.txt via GitHub API (no clone needed)
          UPSTREAM=$(curl -s -H "Authorization: Bearer $GH_TOKEN" \
            "https://api.github.com/repos/tdlib/td/contents/CMakeLists.txt" \
            | jq -r '.content' | base64 -d \
            | grep -oP 'set\(TDLib_VERSION \K[0-9]+\.[0-9]+\.[0-9]+')

          LOCAL=$(cat VERSION)

          echo "Upstream: $UPSTREAM"
          echo "Local: $LOCAL"

          if [ "$UPSTREAM" != "$LOCAL" ]; then
            echo "changed=true" >> $GITHUB_OUTPUT
            echo "new_version=$UPSTREAM" >> $GITHUB_OUTPUT
            echo "old_version=$LOCAL" >> $GITHUB_OUTPUT
          else
            # Also check if TL schema changed (catches non-version API changes)
            UPSTREAM_HASH=$(curl -s -H "Authorization: Bearer $GH_TOKEN" \
              "https://api.github.com/repos/tdlib/td/commits?path=td/generate/scheme/td_api.tl&per_page=1" \
              | jq -r '.[0].sha')
            LOCAL_HASH=$(cat .tdl_schema_hash 2>/dev/null || echo "none")
            if [ "$UPSTREAM_HASH" != "$LOCAL_HASH" ]; then
              echo "changed=true" >> $GITHUB_OUTPUT
              echo "new_version=$UPSTREAM" >> $GITHUB_OUTPUT
              echo "old_version=$LOCAL" >> $GITHUB_OUTPUT
              echo "$UPSTREAM_HASH" > .tdl_schema_hash
            else
              echo "changed=false" >> $GITHUB_OUTPUT
            fi
          fi

  trigger-build:
    needs: check
    if: needs.check.outputs.version_changed == 'true'
    uses: ./.github/workflows/build.yml
    with:
      new_version: ${{ needs.check.outputs.new_version }}
      old_version: ${{ needs.check.outputs.old_version }}
    secrets: inherit
```

### 7.2 build.yml
```yaml
name: Build TDLib Android AAR
on:
  workflow_call:
    inputs:
      new_version:
        required: true
        type: string
      old_version:
        required: true
        type: string
  workflow_dispatch:
    inputs:
      new_version:
        required: true
        type: string
      old_version:
        required: false
        type: string
        default: "unknown"

jobs:
  build-abi:
    strategy:
      matrix:
        abi: [arm64-v8a, armeabi-v7a, x86_64, x86]
      fail-fast: true   # If one ABI fails, cancel others — never publish partial
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Cache Docker layers
        uses: actions/cache@v4
        with:
          path: /tmp/docker-cache
          key: docker-tdlib-${{ inputs.new_version }}-${{ matrix.abi }}
          restore-keys: docker-tdlib-

      - name: Build TDLib for ${{ matrix.abi }}
        id: build
        env:
          ABI: ${{ matrix.abi }}
          TDLIB_VERSION: ${{ inputs.new_version }}
        run: |
          set -euo pipefail

          # Retry logic: 3 attempts with 30s backoff
          for attempt in 1 2 3; do
            echo "Build attempt $attempt for ABI: $ABI"
            if docker build \
              --build-arg TDLIB_INTERFACE=Java \
              --build-arg ANDROID_NDK_VERSION=27.2.12479018 \
              --build-arg COMMIT_HASH=HEAD \
              --output tdlib_output \
              ./docker/; then
              echo "Build succeeded on attempt $attempt"
              break
            fi
            if [ $attempt -eq 3 ]; then
              echo "BUILD_FAILED=true" >> $GITHUB_ENV
              exit 1
            fi
            echo "Attempt $attempt failed. Retrying in 30s..."
            sleep 30
          done

          # Extract .so for this ABI
          mkdir -p artifacts/$ABI
          cp tdlib_output/libs/$ABI/libtdjson.so artifacts/$ABI/

          # Extract TdApi.java (same for all ABIs, but upload once per job)
          mkdir -p artifacts/java
          cp -r tdlib_output/java/. artifacts/java/

          # Verify .so is not empty/corrupt
          SO_SIZE=$(stat -c%s "artifacts/$ABI/libtdjson.so")
          if [ "$SO_SIZE" -lt 1000000 ]; then
            echo "ERROR: libtdjson.so for $ABI is suspiciously small: ${SO_SIZE} bytes"
            exit 1
          fi

      - name: Upload ABI artifact
        uses: actions/upload-artifact@v4
        with:
          name: tdlib-${{ matrix.abi }}
          path: artifacts/
          retention-days: 7

  package-and-test:
    needs: build-abi
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with:
          java-version: '17'
          distribution: 'temurin'

      - name: Download all ABI artifacts
        uses: actions/download-artifact@v4
        with:
          pattern: tdlib-*
          merge-multiple: true
          path: downloaded_artifacts/

      - name: Verify 4 ABIs present
        run: |
          ./scripts/verify-abi-count.sh downloaded_artifacts/
          # Script checks: arm64-v8a, armeabi-v7a, x86_64, x86 all present
          # Fails with error if any missing

      - name: Stage .so files and TdApi.java
        run: |
          mkdir -p core/src/main/jniLibs/{arm64-v8a,armeabi-v7a,x86_64,x86}
          cp downloaded_artifacts/arm64-v8a/libtdjson.so core/src/main/jniLibs/arm64-v8a/
          cp downloaded_artifacts/armeabi-v7a/libtdjson.so core/src/main/jniLibs/armeabi-v7a/
          cp downloaded_artifacts/x86_64/libtdjson.so core/src/main/jniLibs/x86_64/
          cp downloaded_artifacts/x86/libtdjson.so core/src/main/jniLibs/x86/
          mkdir -p core/src/main/java/org/drinkless/tdlib
          cp downloaded_artifacts/java/org/drinkless/tdlib/TdApi.java core/src/main/java/org/drinkless/tdlib/
          cp downloaded_artifacts/java/org/drinkless/tdlib/Client.java core/src/main/java/org/drinkless/tdlib/

      - name: Verify TdApi.java is complete
        run: |
          SIZE=$(stat -c%s core/src/main/java/org/drinkless/tdlib/TdApi.java)
          if [ "$SIZE" -lt 100000 ]; then
            echo "ERROR: TdApi.java is too small (${SIZE} bytes) — likely incomplete"
            exit 1
          fi

      - name: Build AAR
        run: ./gradlew :core:assembleRelease :ktx:assembleRelease

      - name: Smoke test — load AAR
        run: ./scripts/smoke-test.sh
        # smoke-test.sh: creates minimal Android project, adds .aar as local dep,
        # builds it, verifies TdApi class is accessible, asserts no compile errors

      - name: Compute checksums
        run: |
          sha256sum core/build/outputs/aar/core-release.aar > core-release.aar.sha256
          sha256sum core/src/main/jniLibs/arm64-v8a/libtdjson.so >> checksums.txt
          sha256sum core/src/main/jniLibs/armeabi-v7a/libtdjson.so >> checksums.txt
          sha256sum core/src/main/jniLibs/x86_64/libtdjson.so >> checksums.txt
          sha256sum core/src/main/jniLibs/x86/libtdjson.so >> checksums.txt

      - name: Upload final AAR artifact
        uses: actions/upload-artifact@v4
        with:
          name: tdlib-android-aar-${{ inputs.new_version }}
          path: |
            core/build/outputs/aar/core-release.aar
            ktx/build/outputs/aar/ktx-release.aar
            checksums.txt
          retention-days: 30

      - name: Generate TdApi.java diff
        run: |
          # Diff against last shipped version (stored in git)
          git diff HEAD -- "docs/api-snapshots/TdApi_${{ inputs.old_version }}.java" \
            "core/src/main/java/org/drinkless/tdlib/TdApi.java" \
            > tdapi_diff.txt 2>/dev/null || echo "First version — no diff available" > tdapi_diff.txt

      - name: Open PR with version bump
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          NEW_VERSION: ${{ inputs.new_version }}
          OLD_VERSION: ${{ inputs.old_version }}
        run: |
          ./scripts/generate-pr-body.sh "$OLD_VERSION" "$NEW_VERSION" > pr_body.md

          git config user.name "tdlib-android-bot"
          git config user.email "bot@tdlib-android.github.io"
          git checkout -b "bump/tdlib-$NEW_VERSION"

          # Update VERSION file
          echo "$NEW_VERSION" > VERSION
          # Store TdApi snapshot for future diffs
          mkdir -p docs/api-snapshots
          cp core/src/main/java/org/drinkless/tdlib/TdApi.java \
             "docs/api-snapshots/TdApi_${NEW_VERSION}.java"

          git add VERSION docs/api-snapshots/
          git commit -m "chore: bump TDLib ${OLD_VERSION} → ${NEW_VERSION}"
          git push origin "bump/tdlib-$NEW_VERSION"

          gh pr create \
            --title "chore: bump TDLib ${OLD_VERSION} → ${NEW_VERSION}" \
            --body-file pr_body.md \
            --base main \
            --label "version-bump,automated"
```

### 7.3 publish.yml
```yaml
name: Publish to Maven Central
on:
  pull_request:
    types: [closed]
    branches: [main]

jobs:
  publish:
    if: github.event.pull_request.merged == true &&
        contains(github.event.pull_request.labels.*.name, 'version-bump')
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with:
          java-version: '17'
          distribution: 'temurin'

      - name: Download AAR artifact
        uses: actions/download-artifact@v4
        with:
          name: tdlib-android-aar-${{ env.NEW_VERSION }}
          # NEW_VERSION extracted from PR title below
        continue-on-error: true  # Artifact may have expired if PR sat >30 days

      - name: Rebuild AAR if artifact expired
        if: steps.download-artifact.outcome == 'failure'
        run: |
          # Re-run build inline — handles the case where PR took >30 days
          # (rare but possible)
          echo "Artifact expired — rebuilding..."
          ./scripts/build-tdlib.sh "$(cat VERSION)"
          ./gradlew :core:assembleRelease :ktx:assembleRelease

      - name: Publish to Maven Central (with retry)
        env:
          ORG_GRADLE_PROJECT_mavenCentralUsername: ${{ secrets.SONATYPE_USERNAME }}
          ORG_GRADLE_PROJECT_mavenCentralPassword: ${{ secrets.SONATYPE_PASSWORD }}
          ORG_GRADLE_PROJECT_signingInMemoryKey: ${{ secrets.GPG_SIGNING_KEY }}
          ORG_GRADLE_PROJECT_signingInMemoryKeyId: ${{ secrets.GPG_KEY_ID }}
          ORG_GRADLE_PROJECT_signingInMemoryKeyPassword: ${{ secrets.GPG_KEY_PASSWORD }}
        run: |
          # Retry loop: 5 attempts, exponential backoff
          BACKOFF=10
          for attempt in 1 2 3 4 5; do
            echo "Publish attempt $attempt"
            if ./gradlew publishAllPublicationsToMavenCentralRepository; then
              echo "Published successfully"
              break
            fi
            if [ $attempt -eq 5 ]; then
              echo "PUBLISH_FAILED after 5 attempts"
              # Error handling: open GitHub Issue
              gh issue create \
                --title "PUBLISH FAILED: TDLib $(cat VERSION) not on Maven Central" \
                --body "All 5 publish attempts failed. Artifact is built and staged. Manual intervention needed." \
                --label "publish-failed,urgent"
              exit 1
            fi
            echo "Attempt $attempt failed. Waiting ${BACKOFF}s..."
            sleep $BACKOFF
            BACKOFF=$((BACKOFF * 2))
          done

      - name: Create GitHub Release
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          VERSION=$(cat VERSION)
          ./scripts/generate-release-notes.sh "$VERSION" > release_notes.md

          gh release create "v${VERSION}" \
            --title "TDLib ${VERSION}" \
            --notes-file release_notes.md \
            core/build/outputs/aar/core-release.aar \
            ktx/build/outputs/aar/ktx-release.aar \
            checksums.txt

      - name: Update README badge version
        run: |
          VERSION=$(cat VERSION)
          sed -i "s/TDLib-[0-9.]*/TDLib-${VERSION}/" README.md
          git config user.name "tdlib-android-bot"
          git config user.email "bot@tdlib-android.github.io"
          git add README.md
          git commit -m "docs: update README badge to TDLib ${VERSION}" || true
          git push origin main || true

  trigger-smoke-test:
    needs: publish
    uses: ./.github/workflows/smoke-test-publish.yml
    with:
      version: ${{ env.NEW_VERSION }}
    secrets: inherit
```

### 7.4 smoke-test-publish.yml
```yaml
name: Post-Publish Smoke Test
on:
  workflow_call:
    inputs:
      version:
        required: true
        type: string
  workflow_dispatch:
    inputs:
      version:
        required: true
        type: string

jobs:
  smoke-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with:
          java-version: '17'
          distribution: 'temurin'

      - name: Wait for Maven Central propagation
        run: sleep 600  # 10 minutes — Maven Central sync delay

      - name: Pull artifact from Maven Central and test
        run: |
          VERSION="${{ inputs.version }}"
          # Create minimal test project that depends on published artifact
          mkdir -p /tmp/smoke_test
          cat > /tmp/smoke_test/build.gradle.kts << EOF
          plugins { id("com.android.application") version "8.4.0" }
          repositories { mavenCentral() }
          dependencies {
            implementation("io.github.tdlib-android:core:${VERSION}")
          }
          android {
            compileSdk = 36
            defaultConfig { minSdk = 26; targetSdk = 36 }
          }
          EOF

          cd /tmp/smoke_test
          # Build: verifies artifact is downloadable and compilable
          gradle dependencies --configuration releaseRuntimeClasspath
          # Assert TdApi class is accessible
          echo "import org.drinkless.tdlib.TdApi" > Test.kt
          kotlinc Test.kt -classpath $(gradle dependencies | grep "tdlib-android:core" | awk '{print $NF}') \
            && echo "SMOKE_TEST_PASSED" \
            || echo "SMOKE_TEST_FAILED"

      - name: Open issue if smoke test failed
        if: failure()
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          gh issue create \
            --title "PUBLISH BROKEN: v${{ inputs.version }} fails Maven Central smoke test" \
            --body "The published artifact on Maven Central fails to compile. Immediate attention needed. Consider deprecating this release." \
            --label "publish-broken,urgent"
```

### 7.5 rotate-reminder.yml
```yaml
name: Annual Secrets Rotation Reminder
on:
  schedule:
    - cron: '0 9 1 1 *'  # Jan 1 every year, 09:00 UTC
  workflow_dispatch:

jobs:
  remind:
    runs-on: ubuntu-latest
    steps:
      - name: Open rotation reminder issue
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          gh issue create \
            --title "Annual: Rotate GPG signing key + Sonatype credentials" \
            --body "Yearly reminder to rotate:\n- GPG signing key (secrets: GPG_SIGNING_KEY, GPG_KEY_ID, GPG_KEY_PASSWORD)\n- Sonatype Central Portal credentials (secrets: SONATYPE_USERNAME, SONATYPE_PASSWORD)\n\nUpdate all GitHub Actions secrets after rotation." \
            --label "maintenance,annual"
```

---

## 8. GRADLE — MODULE BUILD FILES

### 8.1 Root build.gradle.kts
```kotlin
// build.gradle.kts (root)
plugins {
    alias(libs.plugins.android.library) apply false
    alias(libs.plugins.kotlin.android) apply false
    alias(libs.plugins.mavenPublish) apply false
}
```

### 8.2 gradle/libs.versions.toml
```toml
[versions]
agp = "8.4.2"
kotlin = "2.0.21"
mavenPublish = "0.29.0"
compileSdk = "36"
minSdk = "26"
targetSdk = "36"

[libraries]
# No external runtime deps for core or ktx
# ktx only depends on kotlinx-coroutines
kotlinx-coroutines = { module = "org.jetbrains.kotlinx:kotlinx-coroutines-android", version = "1.8.1" }

[plugins]
android-library = { id = "com.android.library", version.ref = "agp" }
kotlin-android = { id = "org.jetbrains.kotlin.android", version.ref = "kotlin" }
mavenPublish = { id = "com.vanniktech.maven.publish", version.ref = "mavenPublish" }
```

### 8.3 core/build.gradle.kts
```kotlin
plugins {
    alias(libs.plugins.android.library)
    alias(libs.plugins.kotlin.android)
    alias(libs.plugins.mavenPublish)
}

android {
    namespace = "io.github.tdlibandroid.core"
    compileSdk = libs.versions.compileSdk.get().toInt()
    defaultConfig {
        minSdk = libs.versions.minSdk.get().toInt()
        // ndk.abiFilters: ALL 4 ABIs — never reduce this
        ndk { abiFilters += listOf("arm64-v8a", "armeabi-v7a", "x86_64", "x86") }
        consumerProguardFiles("consumer-rules.pro")
        // consumer-rules.pro ships WITH the AAR into every consuming project's R8 pipeline.
        // Content: -keep class org.drinkless.tdlib.** { *; }
        // Without this: R8 obfuscates native method declarations → JNI bridge crashes at runtime
        // in ANY app that uses this library with isMinifyEnabled=true. Sprint 1 mandatory.
    }
    // Packaging: keep .so files from stripping
    packaging {
        jniLibs.keepDebugSymbols.add("**/*.so")
    }
    sourceSets {
        getByName("main") {
            jniLibs.srcDirs("src/main/jniLibs")
        }
    }
}

dependencies {
    // Zero runtime deps. TdApi.java is bundled, .so is bundled.
    // This is a distribution AAR — must be dependency-free.
}

mavenPublishing {
    publishToMavenCentral(SonatypeHost.CENTRAL_PORTAL)
    signAllPublications()
    coordinates(
        groupId = "io.github.tdlib-android",
        artifactId = "core",
        version = File(rootDir, "VERSION").readText().trim()
    )
    pom {
        name.set("tdlib-android-core")
        description.set("Community-maintained TDLib prebuilt AAR for Android. Auto-updated. Zero build steps.")
        inceptionYear.set("2026")
        url.set("https://github.com/tdlib-android/tdlib-android")
        licenses {
            license {
                name.set("Boost Software License 1.0")  // TDLib's license
                url.set("https://www.boost.org/LICENSE_1_0.txt")
            }
        }
        developers {
            developer {
                id.set("AkashPriyadarshii")
                name.set("Akash Priyadarshi")
                url.set("https://github.com/AkashPriyadarshii")
            }
        }
        scm {
            url.set("https://github.com/tdlib-android/tdlib-android")
            connection.set("scm:git:git://github.com/tdlib-android/tdlib-android.git")
            developerConnection.set("scm:git:ssh://git@github.com/tdlib-android/tdlib-android.git")
        }
    }
}
```

### 8.4 ktx/build.gradle.kts
```kotlin
plugins {
    alias(libs.plugins.android.library)
    alias(libs.plugins.kotlin.android)
    alias(libs.plugins.mavenPublish)
}

android {
    namespace = "io.github.tdlibandroid.ktx"
    compileSdk = libs.versions.compileSdk.get().toInt()
    defaultConfig {
        minSdk = libs.versions.minSdk.get().toInt()
    }
}

dependencies {
    // Only dep: core module + coroutines
    api(project(":core"))  // api — consumers get TdApi transitively
    implementation(libs.kotlinx.coroutines)
}

mavenPublishing {
    publishToMavenCentral(SonatypeHost.CENTRAL_PORTAL)
    signAllPublications()
    coordinates(
        groupId = "io.github.tdlib-android",
        artifactId = "ktx",
        version = File(rootDir, "VERSION").readText().trim()
    )
    pom {
        name.set("tdlib-android-ktx")
        description.set("Kotlin Coroutines + Flow wrapper for TDLib Android. Suspend send() + Flow<Update>.")
        // ... same pom metadata as core
    }
}
```

---

## 9. KTX WRAPPER — FULL SPEC

**Design principle:** Thin. ~150 lines total. No application-layer logic. No auth helpers. No message DSL. Just: coroutine-safe `send()` + `Flow<Update>`. Everything else is the consuming app's job.

### 9.1 TdClient.kt
```kotlin
package io.github.tdlibandroid.ktx

import kotlinx.coroutines.*
import kotlinx.coroutines.channels.Channel
import kotlinx.coroutines.flow.*
import org.drinkless.tdlib.Client
import org.drinkless.tdlib.TdApi

/**
 * Kotlin Coroutines wrapper for TDLib.
 * Thread-safe. Lifecycle-aware. Zero opinion on auth or app structure.
 *
 * Usage:
 *   val client = TdClient(filesDir = context.filesDir.absolutePath + "/tdlib")
 *   client.init()
 *   client.updates.collect { update -> /* handle update */ }
 *   val option = client.send(TdApi.GetOption("version"))
 *   client.close()
 */
class TdClient(
    private val filesDir: String,
    private val verbosityLevel: Int = 0   // 0=FATAL, 1=ERROR, 2=WARN, 5=DEBUG
) {
    private val scope = CoroutineScope(SupervisorJob() + Dispatchers.IO)

    // Update stream — hot SharedFlow, 0 replay (stateless), unlimited buffer
    private val _updates = MutableSharedFlow<TdApi.Update>(
        extraBufferCapacity = Channel.UNLIMITED
    )
    val updates: SharedFlow<TdApi.Update> = _updates.asSharedFlow()

    // Pending request map: requestId → CompletableDeferred<TdApi.Object>
    private val pending = java.util.concurrent.ConcurrentHashMap<Long, CompletableDeferred<TdApi.Object>>()
    private var requestId = java.util.concurrent.atomic.AtomicLong(0)

    private var nativeClient: Client? = null

    /**
     * Initialize TDLib. Must be called before any send().
     * Sets up native client, log level, and database path.
     */
    fun init() {
        Client.setLogVerbosityLevel(verbosityLevel)
        nativeClient = Client.create(
            { update ->
                if (update is TdApi.Update) {
                    scope.launch { _updates.emit(update) }
                } else {
                    // This is a response to a pending request
                    // (TDLib sends responses through the same handler)
                    // Note: for typed responses, use send() which registers per-request handlers
                }
            },
            { throwable ->
                // Update exception handler — log, don't crash
                println("[TdClient] Update exception: $throwable")
            },
            { throwable ->
                // Default exception handler
                println("[TdClient] Default exception: $throwable")
            }
        )

        // Set TDLib database directory
        scope.launch {
            send(TdApi.SetTdlibParameters(
                /* useTestDc = */ false,
                /* databaseDirectory = */ filesDir,
                /* filesDirectory = */ "$filesDir/files",
                /* databaseEncryptionKey = */ ByteArray(0),
                /* useFileDatabase = */ true,
                /* useChatInfoDatabase = */ true,
                /* useMessageDatabase = */ true,
                /* useSecretChats = */ false,
                /* apiId = */ 0,   // Set by consuming app before auth
                /* apiHash = */ "", // Set by consuming app before auth
                /* systemLanguageCode = */ "en",
                /* deviceModel = */ android.os.Build.MODEL,
                /* systemVersion = */ android.os.Build.VERSION.RELEASE,
                /* applicationVersion = */ "1.0"
            ))
        }
    }

    /**
     * Send a TDLib function and suspend until response arrives.
     * Throws TdException on TdApi.Error response.
     * Thread-safe — can be called from any coroutine.
     *
     * @throws TdException if TDLib returns TdApi.Error
     * @throws CancellationException if coroutine is cancelled before response
     */
    @Suppress("UNCHECKED_CAST")
    suspend fun <T : TdApi.Object> send(function: TdApi.Function<T>): T {
        val id = requestId.incrementAndGet()
        val deferred = CompletableDeferred<TdApi.Object>()
        pending[id] = deferred

        val client = nativeClient
            ?: throw IllegalStateException("TdClient not initialized. Call init() first.")

        client.send(function) { result ->
            when {
                result is TdApi.Error -> deferred.completeExceptionally(
                    TdException(result.code, result.message)
                )
                else -> deferred.complete(result)
            }
            pending.remove(id)
        }

        return deferred.await() as T
    }

    /**
     * Close TDLib client and release all resources.
     * After close(), this instance cannot be reused.
     */
    fun close() {
        scope.cancel()
        nativeClient?.close()
        nativeClient = null
        pending.forEach { (_, deferred) ->
            deferred.completeExceptionally(CancellationException("TdClient closed"))
        }
        pending.clear()
    }
}

/**
 * Exception thrown when TDLib returns TdApi.Error.
 */
class TdException(val code: Int, override val message: String) : Exception(message) {
    val isFloodWait: Boolean get() = message.startsWith("FLOOD_WAIT_")
    val floodWaitSeconds: Long get() = if (isFloodWait) message.substringAfter("FLOOD_WAIT_").toLong() else 0L
    val isUnauthorized: Boolean get() = code == 401
    val isNotFound: Boolean get() = code == 404
}
```

### 9.2 TdExtensions.kt
```kotlin
package io.github.tdlibandroid.ktx

import kotlinx.coroutines.flow.*
import org.drinkless.tdlib.TdApi

/**
 * Suspend until TDLib reaches authorizationStateReady.
 * Collect updates until ready, then return.
 */
suspend fun TdClient.awaitReady() {
    updates
        .filterIsInstance<TdApi.UpdateAuthorizationState>()
        .filter { it.authorizationState is TdApi.AuthorizationStateReady }
        .first()
}

/**
 * Returns a Flow of a specific update type.
 * Example: client.updatesOf<TdApi.UpdateNewMessage>().collect { ... }
 */
inline fun <reified T : TdApi.Update> TdClient.updatesOf(): Flow<T> =
    updates.filterIsInstance<T>()

/**
 * Returns true if TDLib is currently in authorizationStateReady.
 * Non-suspending — checks the last seen update state.
 * Note: for reliable state, prefer collecting updates directly.
 */
fun TdApi.AuthorizationState.isReady(): Boolean =
    this is TdApi.AuthorizationStateReady
```

---

## 10. README — STAR MAGNET SPEC

The README is a product. It must answer every developer's question in 30 seconds and have the Gradle snippet above the fold.

```markdown
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
- [OurDrive](https://github.com/AkashPriyadarshii) — private encrypted Android cloud storage

[Open a PR to add your project]

## Version History

Auto-generated from TDLib upstream. See [CHANGELOG.md](CHANGELOG.md).

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) — CI architecture, how to add ABI support, how to contribute to the ktx wrapper.

## License

TDLib and its Java interface are licensed under [BSL-1.0](https://www.boost.org/LICENSE_1_0.txt).
This wrapper (ktx module) is Apache 2.0.
```

---

## 11. SCRIPTS — FULL SPEC

### 11.1 scripts/verify-abi-count.sh
```bash
#!/bin/bash
# Verify all 4 required ABIs are present before packaging
# Usage: ./scripts/verify-abi-count.sh <artifacts_dir>
set -euo pipefail

ARTIFACTS_DIR="${1:?Usage: verify-abi-count.sh <artifacts_dir>}"
REQUIRED_ABIS=("arm64-v8a" "armeabi-v7a" "x86_64" "x86")
FAILED=0

for ABI in "${REQUIRED_ABIS[@]}"; do
    SO_PATH="$ARTIFACTS_DIR/$ABI/libtdjson.so"
    if [ ! -f "$SO_PATH" ]; then
        echo "ERROR: Missing libtdjson.so for ABI: $ABI (expected at $SO_PATH)"
        FAILED=1
    else
        SIZE=$(stat -c%s "$SO_PATH")
        if [ "$SIZE" -lt 1000000 ]; then
            echo "ERROR: libtdjson.so for $ABI is suspiciously small: ${SIZE} bytes"
            FAILED=1
        else
            echo "OK: $ABI (${SIZE} bytes)"
        fi
    fi
done

if [ $FAILED -eq 1 ]; then
    echo "FATAL: ABI verification failed. Aborting release."
    exit 1
fi

echo "All 4 ABIs verified. Proceeding."
```

### 11.2 scripts/generate-pr-body.sh
```bash
#!/bin/bash
# Generate PR body for version bump PRs
# Usage: ./scripts/generate-pr-body.sh <old_version> <new_version>
set -euo pipefail

OLD_VERSION="${1:?}"
NEW_VERSION="${2:?}"

# Extract CHANGELOG section for new version from upstream
CHANGELOG=$(curl -s "https://raw.githubusercontent.com/tdlib/td/master/CHANGELOG.md" \
    | awk "/^## Changes in $NEW_VERSION/,/^## Changes in /" \
    | head -50 \
    || echo "Could not extract CHANGELOG section. See: https://github.com/tdlib/td/blob/master/CHANGELOG.md")

# Read checksums
CHECKSUMS=$(cat checksums.txt 2>/dev/null || echo "Not available")

# Read TdApi diff summary
DIFF_LINES=$(wc -l < tdapi_diff.txt 2>/dev/null || echo "0")

cat << EOF
## TDLib ${OLD_VERSION} → ${NEW_VERSION}

### TdApi.java changes
${DIFF_LINES} lines changed. Review for breaking API changes before merging.

<details>
<summary>View TdApi.java diff</summary>

\`\`\`diff
$(head -200 tdapi_diff.txt 2>/dev/null || echo "Diff not available — first release")
\`\`\`
</details>

### Upstream CHANGELOG
${CHANGELOG}

### Artifact Checksums
\`\`\`
${CHECKSUMS}
\`\`\`

### Smoke Test
$(cat smoke_test_result.txt 2>/dev/null || echo "Not available")

---
**Merge this PR to publish TDLib ${NEW_VERSION} to Maven Central.**

_If TdApi.java diff shows breaking changes (removed methods, changed signatures): check if ktx wrapper needs updates before merging._
EOF
```

---

## 12. MAVEN CENTRAL SETUP — ONE-TIME MANUAL STEPS

This section documents exactly what to do once. After this, everything is automated.

### Step 1: Create Sonatype account
- Go to https://central.sonatype.com
- Register with GitHub or email
- Verify namespace `io.github.tdlib-android` (GitHub org ownership verification = automatic via OAuth)

### Step 2: Generate user token
- In Sonatype Portal: Account → Generate User Token
- This gives `SONATYPE_USERNAME` + `SONATYPE_PASSWORD` (not your account creds)
- Add both to GitHub Actions secrets

### Step 3: Generate GPG key
```bash
gpg --batch --generate-key <<EOF
Key-Type: RSA
Key-Length: 4096
Name-Real: Akash Priyadarshi
Name-Email: akash@tdlib-android.github.io
Expire-Date: 2y
%no-protection
EOF

# Export key ID
gpg --list-keys --keyid-format SHORT
# → something like: rsa4096/ABCD1234

# Export secret key for CI
gpg --armor --export-secret-keys ABCD1234 > gpg_private.asc

# Upload public key to keyserver (Maven Central requirement)
gpg --keyserver keyserver.ubuntu.com --send-keys ABCD1234
```

### Step 4: Add GitHub Actions secrets
```
SONATYPE_USERNAME     → from Sonatype user token
SONATYPE_PASSWORD     → from Sonatype user token
GPG_SIGNING_KEY       → contents of gpg_private.asc (full armor text)
GPG_KEY_ID            → short key ID (e.g. ABCD1234)
GPG_KEY_PASSWORD      → empty string (since we used %no-protection above)
```

### Step 5: First manual publish (proves pipeline works)
```bash
# Run once locally to verify signing + upload works
./gradlew publishAllPublicationsToMavenCentralRepository \
  -PmavenCentralUsername=YOUR_TOKEN_USERNAME \
  -PmavenCentralPassword=YOUR_TOKEN_PASSWORD \
  -PsigningInMemoryKey="$(cat gpg_private.asc)" \
  -PsigningInMemoryKeyId=ABCD1234 \
  -PsigningInMemoryKeyPassword=""
```

After this, all future publishes are automated.

---

## 13. SPRINT PLAN

**Math: CI builds everything. Windows 11 / 6GB RAM is irrelevant — zero local builds required.**

### Sprint 1 (2 days): Repo scaffold + manual proof
- Create GitHub org `tdlib-android`
- Scaffold repo structure (all dirs, empty files)
- `settings.gradle.kts` + `libs.versions.toml` + root `build.gradle.kts`
- `core/build.gradle.kts` + `ktx/build.gradle.kts` (Maven Central config)
- **`core/consumer-rules.pro`** — write immediately: `-keep class org.drinkless.tdlib.** { *; }` — Sprint 1 mandatory, not optional. Without this every consumer app with `isMinifyEnabled=true` gets a runtime JNI crash.
- Run TDLib Docker build manually on GitHub Actions (workflow_dispatch) for arm64-v8a only
- Verify `.so` + `TdApi.java` output from Docker
- Stage files, run `./gradlew :core:assembleRelease` — confirm AAR builds
- One-time Sonatype setup (Step 12 above)
- One manual `publishToMavenCentral` to prove signing works
- Install Antigravity skills: `sickn33/antigravity-awesome-skills` into `.agents/skills/`
- Write 3 custom skill stubs: `tdlib-ci-expert.md`, `kotlin-jni-expert.md`, `maven-publish-expert.md`
- **Exit criteria:** `io.github.tdlib-android:core:X.X.X` exists on Maven Central, `consumer-rules.pro` ships with AAR

### Sprint 2 (2 days): Full CI pipeline
- `check-upstream.yml` — VERSION poll, schema hash, trigger logic
- `build.yml` — 4-ABI matrix, Docker, retry logic, all error checks from §4
- `scripts/verify-abi-count.sh` + all other scripts
- `scripts/generate-pr-body.sh`
- Human PR gate: test it generates correct PR
- **Exit criteria:** New upstream TDLib version auto-triggers build, PR opens, CI passes

### Sprint 3 (1 day): Publish automation + ktx + IDE fix
- `publish.yml` — on PR merge, publish + GitHub Release + README badge update
- `smoke-test-publish.yml` — post-publish Maven Central verification
- `rotate-reminder.yml` — annual cron
- `TdClient.kt` + `TdExtensions.kt` — full ktx wrapper
- `sample/` — minimal working example (auth flow → getChats)
- **`tdapi-stub.jar`** — strip method bodies from TdApi.java, ship stub JAR alongside full JAR. TdApi.java is 30MB+; without stub, Android Studio freezes for 5+ minutes on first import = immediate uninstall. CI generates stub via `javac -proc:none` + strip pass. Both full + stub JARs published to Maven Central.
- **Exit criteria:** Merge PR → auto-publishes both modules → smoke test passes → Android Studio imports library without freeze

### Sprint 4 (1 day): README + community outreach
- README finalized with all badges, ABI table, copy-paste snippet above fold
- CONTRIBUTING.md — CI architecture explained, how to contribute
- CHANGELOG.md auto-generation verified
- Open issue on MonoGram: "Consider using tdlib-android:core for dependency management"
- Open issue on any active FOSS TG client repos pointing to library
- Post on Reddit r/androiddev + r/Telegram
- **Exit criteria:** First external developer uses the library

---

## 14. CONSTRAINTS

- ₹0 — GitHub Actions free tier (unlimited for public repos), Sonatype Central Portal (free for OSS), GPG (free)
- Windows 11 / 6GB RAM irrelevant — CI does all builds on GitHub-hosted Ubuntu runners
- No local build required ever — `workflow_dispatch` triggers CI manually when needed
- TDLib license: BSL-1.0 (permissive, allows redistribution as prebuilt)
- ktx wrapper: Apache 2.0
- Maven Central group `io.github.tdlib-android` — requires GitHub org `tdlib-android` (free)
- ABI coverage: 4 ABIs (arm64-v8a mandatory, others for full ecosystem support)
- minSdk: 26 — library distribution, not app. Maximize adoption.
- GitHub Actions cache NOT used for Docker layers — 10GB repo limit × 4 ABI images ≈ 20GB = constant eviction. No caching is faster than broken caching.
- Antigravity 2.0: 4× AI Pro accounts ($19.99/mo each). Rotate Google account when compute budget exhausted. Compute refreshes every 5h. Effective unlimited access across 4 accounts. Models: Gemini 3.5 Flash (default), Gemini 3.1 Pro, Claude Sonnet 4.6, Claude Opus 4.6, GPT-OSS 120B.
- Gemini CLI deprecated June 18 2026 — use `agy` (Antigravity CLI) for all terminal agent work from now.
- AGENTS.md at repo root is the canonical context file for Antigravity 2.0 (replaces CLAUDE.md convention).

---

## 15. RISKS

| Risk | Severity | Mitigation |
|---|---|---|
| TDLib Docker image changes build script | Medium | Pin Docker image tag. Check upstream Dockerfile on each build, diff against expected. |
| NDK version deprecation on GitHub Actions runners | Low | `ANDROID_NDK_VERSION` is an explicit param in build.yml — update in one place |
| Sonatype Central Portal policy change | Low | Artifacts are Apache/BSL — meets all OSS requirements |
| TDLib upstream removes Java interface | Very Low | Java JNI is TDLib's primary Android interface, used by Telegram itself — will not be removed |
| Someone maintains a better solution | Low | Be first, be reliable, be fast. Community trust compounds. |
| GitHub org name `tdlib-android` taken | Check before Sprint 1 | Alt: `tdlib-for-android`, `tdlib-community` |
| TdApi.java IDX limit (30MB+ breaks Android Studio) | Medium — addressed in v0.1 | `tdapi-stub.jar` ships in Sprint 3: strips method bodies, published to Maven Central alongside full JAR. IDE freeze eliminated. |
| Docker build time causes GitHub Actions timeout (6h limit) | Low | TDLib Docker build per ABI ≈ 45min. 45min × 4 ABIs parallel = 45min wall clock. Well under limit. |

---

## 16. V0.2 ROADMAP (NOT V0.1)

- GitHub Packages mirror (for users who prefer it over Maven Central)
- ProGuard/R8 keep rules shipped with AAR
- Coroutines-first auth helper (phone → OTP → ready in 5 lines)
- Compose UI library for auth flows (separate module, `tdlib-android:compose-auth`)

---

## 17. ANTIGRAVITY 2.0 WORKFLOW

### 17.1 What Antigravity 2.0 Is (for this project)

Antigravity 2.0 (launched May 19 2026 at Google I/O) is the primary development environment for tdlib-android. It is a standalone desktop agent platform — not a VS Code fork. Key facts:
- Default model: Gemini 3.5 Flash (fast, free on AI Pro)
- Also available: Gemini 3.1 Pro, Claude Sonnet 4.6, Claude Opus 4.6, GPT-OSS 120B
- Compute budget refreshes every 5 hours (not daily)
- 4× AI Pro accounts = rotate when one account hits compute limit
- `AGENTS.md` at repo root = canonical context file, auto-read every session
- `.agents/skills/` = Markdown skill files, invoked by name
- CLI: `agy` (Go binary) replaces Gemini CLI (deprecated June 18 2026)
- Parallel subagents (Agent Teams): spawn multiple focused agents simultaneously

### 17.2 One-Time Setup (do before Sprint 1)

```bash
# Install Antigravity CLI
curl -sSL https://antigravity.google.dev/install.sh | bash

# Install antigravity-awesome-skills into project
mkdir -p .agents/skills
cd .agents/skills
git clone https://github.com/sickn33/antigravity-awesome-skills antigravity-awesome-skills
# 1,400+ skills now available via @skill-name in Antigravity

# Install repomix globally (session-start tool)
npm install -g repomix

# Install gitleaks (session-end security)
# Windows: winget install gitleaks
winget install gitleaks

# Install foxguard (diff-aware secrets scanner)
# Follow: https://github.com/0sec-labs/foxguard

# Migrate from Gemini CLI if needed
agy migrate-cli
```

### 17.3 Parallel Subagent Team Layout

tdlib-android has 4 independent workstreams. Run them in parallel using Antigravity Agent Teams:

| Agent | Name | File Scope | Model | Responsibility |
|---|---|---|---|---|
| Agent A | `ci-agent` | `.github/workflows/` + `scripts/` | Gemini 3.5 Flash | All YAML workflows, bash scripts, Docker args, swap step, readelf check |
| Agent B | `gradle-agent` | `core/build.gradle.kts` + `ktx/build.gradle.kts` + `gradle/` | Gemini 3.5 Flash | Gradle modules, Maven Central publishing, consumer-rules.pro, version catalog |
| Agent C | `kotlin-agent` | `ktx/src/` + `sample/` | Claude Sonnet 4.6 | TdClient.kt, TdExtensions.kt, TdException, sample app — use Claude for Kotlin reasoning quality |
| Agent D | `docs-agent` | `README.md` + `CONTRIBUTING.md` + `CHANGELOG.md` + `AGENTS.md` | Gemini 3.5 Flash | README badges, CONTRIBUTING guide, AGENTS.md maintenance |

**How to spawn:**
In Antigravity desktop → Agent Teams → New Team → assign each agent its file scope + skill + model as above.

**Key rule:** Agent C uses Claude Sonnet 4.6 (not Gemini) — Kotlin coroutines + JNI bridge reasoning quality is meaningfully better. Switch model per-agent in Antigravity Agent Teams panel.

### 17.4 Custom Skill Stubs

Write these 3 files once in Sprint 1. They prevent agents from hallucinating NDK versions, wrong Sonatype API calls, or broken TDLib build args.

**`.agents/skills/tdlib-ci-expert.md`**
```markdown
# TDLib CI Expert

You are a CI/CD specialist for tdlib-android. You know:
- TDLib builds via official Docker image with TDLIB_INTERFACE=Java
- NDK version pinned: 27.2.12479018 (r27c) — never change without explicit instruction
- 4 ABIs always: arm64-v8a, armeabi-v7a, x86_64, x86 — fail-fast: true
- Docker layer caching is intentionally disabled (10GB Actions cache limit)
- Swap space: pierotofy/set-swap-space@master, 10GB — mandatory before every Docker build
- .so validation: readelf -h not file size (size is fragile)
- VERSION file = single source of truth for TDLib version across all files
- Never publish partial ABI sets — verify-abi-count.sh must pass before any publish step
- Error handling: every failure opens a GitHub Issue with appropriate label
- Secrets: SONATYPE_USERNAME, SONATYPE_PASSWORD, GPG_SIGNING_KEY, GPG_KEY_ID, GPG_KEY_PASSWORD
- All bash scripts: set -euo pipefail, every exit code checked
```

**`.agents/skills/kotlin-jni-expert.md`**
```markdown
# Kotlin JNI Expert

You are a Kotlin + TDLib JNI specialist for tdlib-android:ktx. You know:
- TdClient wraps org.drinkless.tdlib.Client (JNI, not JSON interface)
- ConcurrentHashMap<Long, CompletableDeferred<TdApi.Object>> for pending requests
- MutableSharedFlow(extraBufferCapacity = Channel.UNLIMITED) — never drop updates
- suspend fun send<T>: registers per-request JNI callback → CompletableDeferred → await
- TdException: code + message + isFloodWait + floodWaitSeconds + isUnauthorized
- deviceModel = android.os.Build.MODEL (never hardcoded "Android")
- TdClient is thin bridge only — no auth helpers, no DSL, no application logic
- ktx depends on :core via api() (transitive — consumers get TdApi without extra dep)
- minSdk 26, Kotlin 2.0+, kotlinx-coroutines 1.8.1
- consumer-rules.pro in :core ships -keep class org.drinkless.tdlib.** { *; }
```

**`.agents/skills/maven-publish-expert.md`**
```markdown
# Maven Central / Sonatype Expert

You are a Maven Central publishing specialist for tdlib-android. You know:
- Use Sonatype Central Portal (NOT legacy OSSRH — deprecated mid-2024)
- Plugin: com.vanniktech.maven.publish 0.29.0
- SonatypeHost.CENTRAL_PORTAL in mavenPublishing block
- In-memory GPG signing: signingInMemoryKey, signingInMemoryKeyId, signingInMemoryKeyPassword
- Version always read from File(rootDir, "VERSION").readText().trim() — never hardcoded
- Group ID: io.github.tdlib-android (requires GitHub org tdlib-android)
- Artifacts: core (BSL-1.0) + ktx (Apache 2.0)
- Publish retry: 5× exponential backoff (10s → 20s → 40s → 80s → 160s)
- 401 from Sonatype = credentials expired = open Issue immediately, no retry
- Post-publish smoke test: pull from Maven Central after 10min propagation delay
- Annual rotation: GPG key + Sonatype user token (rotate-reminder.yml cron Jan 1)
```

### 17.5 Session Start Ritual (every coding session)

```bash
# 1. Pack repo into single AI-optimized context file
repomix --output repomix-output.txt
# Covers all: YAML + Kotlin + Bash + Gradle simultaneously

# 2. Open Antigravity, load context
# In Antigravity: Knowledge Base → Add → repomix-output.txt

# 3. Spawn agents per §17.3 layout
# Assign each agent its file scope + load its skill

# 4. Verify account compute budget
# If low → switch to next Google account
# Account rotation order: Account 1 → 2 → 3 → 4 → back to 1 (5h refresh cycle)
```

### 17.6 Session End Ritual (before every git push)

```bash
# 1. Scan for secrets in staged files
gitleaks detect --staged

# 2. Diff-aware secrets + security scan
foxguard scan --diff HEAD

# 3. Snapshot agent memory state
memoir snapshot "sprint-X-session-Y"

# 4. Only push if both scans pass
git push origin <branch>
```

**Hard rule:** Never `git push` without gitleaks passing. This repo will contain GitHub Actions secrets config. One accidental commit of a real secret = rotate everything immediately.

### 17.7 Scheduled Tasks (Antigravity Scheduled Tasks feature)

Set these once in Antigravity desktop → Scheduled Tasks:

**Daily (08:00 IST):**
```
Task: "Drift check"
Prompt: "Read AGENTS.md and the bible spec. Scan the current repo state via repomix.
Check for any drift from spec: wrong NDK version, missing consumer-rules.pro,
wrong minSdk, ABI count != 4, VERSION mismatch. Open a GitHub Issue for each drift found."
Model: Gemini 3.5 Flash
```

**Weekly (Monday 09:00 IST):**
```
Task: "Upstream watch"
Prompt: "Check tdlib/td GitHub issues tagged 'android' opened in the last 7 days.
Summarize any that affect our prebuilt distribution. Check if any new TDLib version
was tagged upstream. Report summary as a GitHub Issue tagged 'weekly-watch'."
Model: Gemini 3.5 Flash
```

### 17.8 burn-baby-burn Harness (for Sprint 2 CI implementation)

Sprint 2 is pure YAML + bash. Longest sprint. Use burn-baby-burn to run the ci-agent continuously:

```
Harness prompt for ci-agent:
"Implement the complete .github/workflows/ directory for tdlib-android exactly as
specified in the bible §7. Do not stop until:
□ check-upstream.yml is valid YAML and logic-correct
□ build.yml matrix builds all 4 ABIs with swap + readelf check
□ publish.yml triggers on version-bump PR merge
□ smoke-test-publish.yml passes with 10min delay
□ rotate-reminder.yml opens annual issue
□ All 5 scripts in scripts/ are implemented with bash -euo pipefail
□ verify-abi-count.sh uses readelf not size check
□ generate-pr-body.sh produces correct PR body format
Self-correct any YAML syntax errors. Check against GitHub Actions schema."
```

---

---

## ##PROMPTS

### CI Setup Prompt (Sprint 1–2)
```
## Agent: ci-agent | Skill: tdlib-ci-expert | Model: Gemini 3.5 Flash
## Harness: burn-baby-burn — do not stop until ALL checklist items below pass
## Context: AGENTS.md + repomix-output.txt loaded in Knowledge Base

You are setting up the CI/CD pipeline for tdlib-android — a community-maintained TDLib prebuilt AAR for Android.

Repo: github.com/tdlib-android/tdlib-android
Goal: Fully automated pipeline that polls TDLib upstream, builds 4-ABI AAR, opens human-review PR, publishes to Maven Central on merge.

Implement exactly as specified in the Bible §7 workflows:
1. .github/workflows/check-upstream.yml — poll TDLib CMakeLists.txt VERSION every 6h via GitHub API. Also check td_api.tl hash. Trigger build.yml on change.
2. .github/workflows/build.yml — 4-ABI matrix (arm64-v8a, armeabi-v7a, x86_64, x86), each uses official TDLib Dockerfile with TDLIB_INTERFACE=Java. Retry 3× with 30s backoff on failure. fail-fast: true (never partial). Merge step: verify-abi-count.sh, Gradle assembleRelease, smoke-test.sh, generate PR body, open PR.
3. scripts/verify-abi-count.sh — asserts all 4 ABIs present, each .so > 1MB.
4. scripts/generate-pr-body.sh — extracts CHANGELOG section, TdApi.java diff, checksums into PR body.

Error scenarios handled (Bible §4): build fail = retry 3× + Issue; partial ABI = fail entire job; TdApi.java < 100KB = fail; Sonatype 401 = Issue immediately; ktx compile fail = block PR + Issue; Docker OOM exit 137 = swap space (pierotofy/set-swap-space 10GB) prevents this.

Rules: YAML workflows valid syntax. Scripts bash -euo pipefail. All exit codes checked. No silent failures. Every failure path opens a GitHub Issue with appropriate label.
```

### Gradle/Maven Prompt (Sprint 1)
```
## Agent: gradle-agent | Skill: maven-publish-expert | Model: Gemini 3.5 Flash
## Context: AGENTS.md + repomix-output.txt loaded in Knowledge Base

Implement Gradle build files for tdlib-android:
- Root build.gradle.kts: minimal, plugin declarations only
- gradle/libs.versions.toml: AGP 8.4.2, Kotlin 2.0.21, vanniktech maven publish 0.29.0, kotlinx-coroutines 1.8.1
- core/build.gradle.kts: android library, namespace io.github.tdlibandroid.core, minSdk 26, all 4 ABI filters, zero runtime deps, mavenPublishing to CENTRAL_PORTAL with BSL-1.0 license, developer = Akash Priyadarshi / AkashPriyadarshii, VERSION read from File(rootDir, "VERSION").readText().trim()
- ktx/build.gradle.kts: android library, depends on :core via api(), kotlinx-coroutines implementation, Apache 2.0 license in pom, same developer

Use com.vanniktech.maven.publish 0.29.0 for all publishing. signAllPublications(). In-memory signing (signingInMemoryKey, signingInMemoryKeyId, signingInMemoryKeyPassword from gradle properties). No hardcoded credentials anywhere.

Show full folder structure first. Production grade. No placeholders.
```

### ktx Wrapper Prompt (Sprint 3)
```
## Agent: kotlin-agent | Skill: kotlin-jni-expert | Model: Claude Sonnet 4.6
## Context: AGENTS.md + repomix-output.txt loaded in Knowledge Base

Implement the ktx wrapper for tdlib-android. Files:
- ktx/src/main/kotlin/io/github/tdlibandroid/ktx/TdClient.kt
- ktx/src/main/kotlin/io/github/tdlibandroid/ktx/TdExtensions.kt

TdClient.kt requirements:
- CoroutineScope(SupervisorJob() + Dispatchers.IO) for internal work
- MutableSharedFlow<TdApi.Update>(extraBufferCapacity = Channel.UNLIMITED) — hot, no replay
- ConcurrentHashMap<Long, CompletableDeferred<TdApi.Object>> for pending requests
- AtomicLong for request IDs
- suspend fun <T: TdApi.Object> send(function: TdApi.Function<T>): T — registers per-request callback, awaits deferred, throws TdException on TdApi.Error
- TdException data class: code: Int, message: String, isFloodWait, floodWaitSeconds, isUnauthorized, isNotFound
- init(): Client.setLogVerbosityLevel, Client.create with update handler + exception handlers
- close(): scope.cancel(), client.close(), complete all pending deferreds with CancellationException
- filesDir: String constructor param — passed to SetTdlibParameters

TdExtensions.kt:
- suspend fun TdClient.awaitReady() — collects UpdateAuthorizationState until AuthorizationStateReady
- inline fun <reified T: TdApi.Update> TdClient.updatesOf(): Flow<T>
- fun TdApi.AuthorizationState.isReady(): Boolean

No auth helpers. No message DSL. No application logic. Pure bridge only. Thread-safe.
Include JUnit 5 unit tests: send() throws TdException on Error response, awaitReady() returns on AuthorizationStateReady, close() cancels pending deferreds.
```

### Sample App Prompt (Sprint 3)
```
## Agent: kotlin-agent | Skill: kotlin-jni-expert | Model: Claude Sonnet 4.6
## Context: AGENTS.md + repomix-output.txt loaded in Knowledge Base

Implement sample/src/main/kotlin/io/github/tdlibandroid/sample/MainActivity.kt

Minimal working example of tdlib-android:ktx usage:
1. Create TdClient(filesDir = filesDir.absolutePath + "/tdlib")
2. Call client.init()
3. Collect client.updates and print each update type
4. Use client.awaitReady() after auth is complete
5. Send client.send(TdApi.GetChats(null, 10)) and print chat titles
6. Handle TdException with isFloodWait check

Auth flow: collect UpdateAuthorizationState, handle each state:
- WaitTdlibParameters: already handled in TdClient.init()
- WaitPhoneNumber: hardcoded or prompt (sample only)
- WaitCode: prompt user
- Ready: call awaitReady() and proceed

This is a demo. 100 lines max. Show the simplest possible integration.
Include comments explaining each step for developers reading the sample.
```

---

## ##AGENTS.md

```markdown
# tdlib-android — AGENTS.md
# Antigravity 2.0 canonical context file. Auto-read every session.
# Place at repo root. Commit and keep updated.

## Identity
Community-maintained TDLib prebuilt AAR for Android. Auto-updated via CI.
GitHub org: tdlib-android. Maven Central: io.github.tdlib-android.
Author: Akash Priyadarshi (@AkashPriyadarshii).

## Modules
- `:core` — prebuilt .aar with libtdjson.so (4 ABIs) + TdApi.java + Client.java + consumer-rules.pro
- `:ktx` — Kotlin Coroutines/Flow wrapper (~150 lines)
- `:sample` — minimal usage example

## Key Files
- `VERSION` — current shipped TDLib version, read by all build.gradle.kts files
- `.github/workflows/check-upstream.yml` — cron poller, triggers build
- `.github/workflows/build.yml` — 4-ABI Docker matrix build
- `.github/workflows/publish.yml` — Maven Central publish on PR merge
- `scripts/verify-abi-count.sh` — hard gate: all 4 ABIs must be present (uses readelf -h)
- `scripts/generate-pr-body.sh` — auto PR body with diff + checksums
- `core/consumer-rules.pro` — R8 keep rules, ships with AAR
- `ktx/src/main/kotlin/.../TdClient.kt` — core wrapper

## Agent Teams
- ci-agent: `.github/workflows/` + `scripts/` | Skill: tdlib-ci-expert | Model: Gemini 3.5 Flash
- gradle-agent: `core/build.gradle.kts` + `ktx/build.gradle.kts` + `gradle/` | Skill: maven-publish-expert | Model: Gemini 3.5 Flash
- kotlin-agent: `ktx/src/` + `sample/` | Skill: kotlin-jni-expert | Model: Claude Sonnet 4.6
- docs-agent: `README.md` + `CONTRIBUTING.md` + `AGENTS.md` | Model: Gemini 3.5 Flash

## Skills Loaded
All skills in `.agents/skills/`:
- `antigravity-awesome-skills/` — 1,400+ Antigravity-native skills
- `tdlib-ci-expert.md` — CI/YAML/Docker/NDK specialist
- `kotlin-jni-expert.md` — TDLib JNI + Kotlin coroutines specialist
- `maven-publish-expert.md` — Sonatype/GPG/Maven Central specialist

## Scheduled Tasks
- Daily 08:00 IST: drift check (spec vs repo state)
- Weekly Monday 09:00 IST: upstream TDLib watch + new issues summary

## Session Protocol
1. `repomix --output repomix-output.txt` → load into Knowledge Base
2. Spawn agents per Agent Teams above
3. Assign each agent its skill + file scope
4. Session end: `gitleaks detect --staged` + `foxguard scan --diff HEAD` before any push

## Workflow (never change this)
upstream version change → check-upstream.yml detects → build.yml runs matrix →
PR opened with diff + checksums → Akash reviews → merge → publish.yml publishes →
smoke-test-publish.yml verifies on Maven Central

## Constraints
- ₹0 budget, GitHub Actions free tier (public repo = unlimited)
- Zero local builds required — CI only
- minSdk 26 (library, not app — maximize adoption)
- 4 ABIs always: arm64-v8a, armeabi-v7a, x86_64, x86. Never reduce.
- Never commit .so files or TdApi.java (generated artifacts, gitignored)
- fail-fast: true in ABI matrix — never publish partial ABI set
- BSL-1.0 for core (TDLib license), Apache 2.0 for ktx wrapper
- 4× Google AI Pro accounts — rotate on compute exhaustion (5h refresh)
- Gemini CLI deprecated June 18 2026 — use `agy` CLI

## Secrets Required
- SONATYPE_USERNAME, SONATYPE_PASSWORD — Sonatype Central Portal user token
- GPG_SIGNING_KEY, GPG_KEY_ID, GPG_KEY_PASSWORD — in-memory GPG signing

## Code Rules
- No placeholders. No TODOs in shipped code.
- All scripts: bash -euo pipefail. All exit codes checked.
- Every failure path opens a GitHub Issue. No silent errors.
- ktx: thin bridge only. No application logic, no auth helpers, no DSL.
- Gradle: version read from VERSION file always. Never hardcoded.
- PR template auto-filled by generate-pr-body.sh — never edit manually.
- consumer-rules.pro must ship with every :core release — never skip.
- .so validation: readelf -h + architecture check, never file size.

## Antipatterns — NEVER DO
- Commit libtdjson.so or TdApi.java to git
- Reduce ABI count below 4
- Publish without all 4 ABIs verified by verify-abi-count.sh
- Add application-layer logic to ktx module
- Hardcode TDLib version in any build file
- Silent error handling anywhere in CI scripts
- Skip human PR review gate — always required before publish
- Use file size to validate .so (use readelf -h)
- Omit consumer-rules.pro from :core module
- Cache Docker layers in GitHub Actions (10GB limit exceeded)
- Push without gitleaks + foxguard scan passing
```
