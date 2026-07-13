# Changelog

All notable changes to the project are recorded in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and the project follows [Semantic Versioning](https://semver.org/) (the `VERSION`
file at the repository root).

## [0.1.0] — 2026-07-13

### Added
- First release of **morfBeacon**, the shared LAN-supervision library.
- **UDP heartbeat presence** (`Heartbeat`): periodic broadcast of a compact JSON
  datagram (`morfbeacon/1`) on port `45454`, sent to every active interface's
  broadcast address.
- **HTTP `/status` endpoint** (`StatusServer`): serves the app's detailed metrics
  on demand, plus a `/healthz` liveness probe.
- **Metrics extension point** (`IMetricsProvider`, plus a lambda-based
  `FunctionMetricsProvider`) and a one-object façade (`PresenceService`) for a
  ~5-line integration.
- Qt Core + Network only (no Widgets): usable in a headless service.
- `tools/fake_dashboard.py` tester (standard library) and a `morfbeacon_demo`
  example.
- Verified end-to-end on Windows and Linux x64, and integrated into ComponentHub
  and SiteWatch.
