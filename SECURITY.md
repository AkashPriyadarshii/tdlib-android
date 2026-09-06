# Security Policy

tdlib-android takes security and privacy seriously. Report vulnerabilities privately; do not open a public issue.

## Reporting a Vulnerability

1. Open a private advisory: https://github.com/AkashPriyadarshii/tdlib-android/security/advisories
2. Include: affected version, minimal reproduction, impact estimate.

Acknowledgment within 48 hours. Coordinated disclosure after a fix ships.

## Security Expectations

- Data stays on device where the app is offline-capable; no telemetry, no cloud.
- Inputs are treated as hostile at the trust boundary and validated before use.
- The original file is never modified where the tool strips metadata; output goes to app-private storage.