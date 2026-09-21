# tdlib-android — CLAUDE.md
# Canonical instructions for Claude Code / Claude agent sessions.
# Auto-read every session. Keep synchronized with AGENTS.md.

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

## Common Commands
- Gradle assembly: `./gradlew assemble`
- Help / Tasks: `./gradlew help`
- Check working tree: `git status`
- Commit rule: Append `[skip ci]` to doc/config commits unless explicitly triggering a full CI pipeline build

## Agent Teams & Skills
- ci-agent: `.github/workflows/` + `scripts/` | Skill: `tdlib-ci-expert.md`
- gradle-agent: `core/build.gradle.kts` + `ktx/build.gradle.kts` + `gradle/` | Skill: `maven-publish-expert.md`
- kotlin-agent: `ktx/src/` + `sample/` | Skill: `kotlin-jni-expert.md`
- docs-agent: `README.md` + `CONTRIBUTING.md` + `AGENTS.md` + `CLAUDE.md`

## Workflow (Never Change This)
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
- Fully automated release pipeline — zero human in loop for publishing
- Use file size to validate .so (use readelf -h)
- Omit consumer-rules.pro from :core module
- Cache Docker layers in GitHub Actions (10GB limit exceeded)
- Push without gitleaks + foxguard scan passing

- Profile: release-order touch 2026-09-22
