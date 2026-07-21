# Changelog

All notable changes to the project are recorded in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and the project follows [Semantic Versioning](https://semver.org/) (the `VERSION`
file at the repository root).

## [Unreleased]

## [0.4.0] — 2026-07-21

### Added

- **Presence emitter for embedded targets** (`arduino/morfbeacon_emitter.h`).
  Header-only, Arduino + WiFi only, no Qt and no ArduinoJson: an ESP32 announces
  itself with the same `morfbeacon/1` datagram as a Linux or Windows service, and
  is discovered by the same mechanism.

  Until now MeteoHub and GatewayLab were found by TCP probe, which assumes their
  mDNS name is known in advance — the opposite of discovery, and the reason
  static lists were still needed in `morfsystem.json`.

  `buildStatusJson()` produces the matching `/status` document, so an embedded
  device can declare `web_ui` and be linked to like any other service.

- **Why a second implementation exists.** The Qt library cannot run on an ESP32:
  the platform boundary makes this duplication unavoidable, exactly as it does
  for the C++ listener in morfMonitor and the Python one in RaspberryDashboard.
  What is shared is the **protocol**, not the code. Both emitters live in this
  repository on purpose — reading one beside the other is the only guard against
  a silent divergence of the format, and any change to the datagram must touch
  both files.

## [0.3.0] — 2026-07-21

### Added

- **`web_ui` capability — an application can declare that it exposes a web
  interface**, so a consumer can offer a link to it without knowing the
  application at all. This is the capability matching the library was designed
  for, finally exercised: a consumer looks for what a service *can do*, never
  for what it is *called*.

  The split is deliberate and follows *push presence / pull detail*:

  | Where | What |
  | --- | --- |
  | Heartbeat | the capability `web_ui` |
  | `/status` | `web_ui: { path, label, port, description }` |

  The datagram is broadcast by every service every 15 seconds, so it must stay
  short and stable; what may evolve lives behind HTTP and is fetched once. The
  heartbeat does not become a metadata catalogue.

- **New optional `PresenceConfig` fields**: `webUiPath`, `webUiLabel`,
  `webUiDescription`, `webUiPort`. Setting `webUiPath` is the whole declaration.

  The capability is **derived** from `webUiPath` rather than declared
  separately: the detail and the capability that makes it discoverable cannot
  drift apart. Declaring one without the other would produce either an
  undiscoverable interface or a link to nothing.

- `PresenceConfig::kCapabilityWebUi` — use the constant rather than the string,
  so producer and consumer cannot disagree on spelling.

### Compatibility

Purely additive. The protocol stays `morfbeacon/1`: no field is removed or
renamed, the new fields are appended to `PresenceConfig` **after** the existing
ones (positional aggregate initialisation is unaffected), and a service
declaring no interface emits exactly the datagram it emitted before. Consumers
unaware of `web_ui` ignore an unknown capability, as the `capabilities`
mechanism was designed for.

## [0.2.1] — 2026-07-20

### Changed

- Version badge in `README.md` and `README.fr.md` corrected from 0.1.0 to 0.2.0.
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
