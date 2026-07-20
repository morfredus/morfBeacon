# Changelog

All notable changes to the project are recorded in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and the project follows [Semantic Versioning](https://semver.org/) (the `VERSION`
file at the repository root).

## [Unreleased]

### Changed
- Updated integration documentation to use canonical production project paths.

## [0.2.0] — 2026-07-19

### Added
- **`capabilities` field in the UDP heartbeat** (`PresenceConfig::capabilities`).
  Declares what a service *can do*, as opposed to what it *is called*.

  The `app` name is user-modifiable — morfSystem is GPL, anyone may rename an
  application. A consumer matching its peers by name stops seeing them at the
  first rename. Matching a stable capability (`advanced_analysis`,
  `notification`, `storage`…) and merely *displaying* the announced name keeps
  interoperability intact across renames.

  The field is **optional**: a service declaring no capability does not emit it,
  and consumers written before its introduction simply ignore an unknown field.
  Adding it therefore breaks no existing installation, and the protocol version
  stays `morfbeacon/1`.

### Compatibility — verified, not assumed

`capabilities` was inserted **in the middle** of the `PresenceConfig` struct,
which would break any consumer using positional aggregate initialisation. Every
consumer in the ecosystem was checked and re-tested:

| Check | Result |
|---|---|
| How the 5 consumers build `PresenceConfig` | Always default-construct + field assignment — no positional init to break |
| morfNotify rebuilt against 0.2.0 | Builds |
| morfSensor rebuilt against 0.2.0 | Builds |
| Any consumer parsing heartbeats | None — they only emit; the extra JSON field cannot break a reader |
| Vendored copies in consumer repos | Untouched; they keep working until they choose to re-sync |

Prefer **appending** new fields at the end of `PresenceConfig` in future
releases: positional initialisation happens not to be used today, but nothing
guarantees it stays that way.

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
