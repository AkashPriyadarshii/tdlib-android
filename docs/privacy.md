# Privacy Policy — tdlib-android

> Effective Date: September 13, 2026

## 1. Library Privacy Commitments

The `tdlib-android` library artifacts (`io.github.tdlib-android:core` and `io.github.tdlib-android:ktx`) are built and distributed under strict privacy commitments:
- **Zero Telemetry:** No analytics SDKs, advertising IDs, crash beacons, or user tracking are embedded into the compiled AARs.
- **Direct MTProto Connection:** All network calls initiated by TDLib communicate directly between the end-user's device and official Telegram MTProto data centers. No intermediate proxies or maintainer servers intercept or process traffic.
- **Isolated Storage:** Local message caches and SQLite databases remain encrypted within the host application's private app directory (`context.filesDir`).

## 2. Documentation Site Privacy

The documentation website hosted at `tdlib-android.vercel.app`:
- Does not use tracking cookies or behavioral profilers.
- Does not embed third-party analytics trackers or social tracking pixels.
- Minimal HTTP server access logs are processed by Vercel exclusively for security and DDoS defense per Vercel's standard privacy policies.

## 3. Contact & Inquiries

For questions or security disclosure regarding privacy, visit:
- Support & Issues: https://github.com/AkashPriyadarshii/tdlib-android/issues
- Contact Page: https://tdlib-android.vercel.app/contact
- Maintainer: Akash Priyadarshi, Patna, Bihar, India.
