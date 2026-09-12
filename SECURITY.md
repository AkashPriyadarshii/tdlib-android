# Security Policy

## Supported Versions

We provide security fixes and dependency updates for the latest released version of `tdlib-android`.

| Version | Supported          | Notes |
| ------- | ------------------ | ----- |
| Latest  | :white_check_mark: | Active tracking of upstream TDLib releases |
| Older   | :x:                | Update to the latest version |

## Scope & Threat Model

This repository builds and publishes prebuilt Android AARs for TDLib:

1. **Packaging and Build System (`tdlib-android`)**: Build workflows, NDK compilation flags, JNI integration, and `:ktx` Kotlin wrapper code live here. Report vulnerabilities related to ABI packaging, insecure compiler flags, or wrapper defects directly to us.
2. **Upstream TDLib (`tdlib/td`)**: Core Telegram protocol logic, MTProto encryption, and C++ network code belong to upstream TDLib. If you discover a vulnerability in TDLib's core protocol implementation or memory safety in TDLib source, report it to the [upstream TDLib repository](https://github.com/tdlib/td) or to Telegram at `security@telegram.org`.

## Build & Artifact Integrity

- **Deterministic builds**: GitHub Actions builds all binaries in isolated Ubuntu containers using pinned Android NDK `27.2.12479018`.
- **Header validation**: Releases verify every architecture using `readelf -h` to confirm binary headers match target ABIs (`arm64-v8a`, `armeabi-v7a`, `x86_64`, `x86`).
- **No committed binaries**: Git history never stores compiled `.so` binaries or generated `TdApi.java` source.
- **Signed releases**: Maven Central publishes include in-memory GPG signatures and SHA-256 checksums.

## Reporting a Vulnerability

Please do not disclose security issues publicly in GitHub Issues or Discussions.

1. **GitHub Private Vulnerability Report (Preferred)**:
   Submit an advisory report through the **Security** tab of this repository under [Advisories](https://github.com/tdlib-android/tdlib-android/security/advisories/new).
2. **Direct Contact**:
   Contact Akash Priyadarshi via GitHub ([@AkashPriyadarshii](https://github.com/AkashPriyadarshii)).

Include the following in your report:
- Affected component (`:core`, `:ktx`, or CI/CD scripts)
- Clear reproduction steps or proof-of-concept
- Potential impact and exploitation scenario

## Response Process

- **Acknowledgement**: Within 48 hours.
- **Triage & Patch**: We test and apply fixes on an isolated branch.
- **Release**: We publish the fix with a new release and credit the reporter in release notes (unless anonymity is requested).
