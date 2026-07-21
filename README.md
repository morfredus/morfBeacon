# morfBeacon

*Read in another language: **English** (this document) · [Français](README.fr.md).*

[![Version](https://img.shields.io/badge/version-0.4.0-blue)](CHANGELOG.md)
![C++](https://img.shields.io/badge/C%2B%2B-17-00599C?logo=cplusplus)
![Qt](https://img.shields.io/badge/Qt-6-41CD52?logo=qt)
![Build](https://img.shields.io/badge/CMake-3.21+-064F8C?logo=cmake)
![License](https://img.shields.io/badge/License-GPL--3.0--only-blue)

**Shared C++ library for LAN supervision of desktop applications.**

morfBeacon lets an application (ComponentHub, SiteWatch, GatewayLab, and future
tools) **announce its presence** on the local network and **expose its metrics**
to a supervisor (RaspberryDashboard), in a few lines of code.

## Principle: *push presence / pull detail*

Two distinct needs, two mechanisms:

| Need | Mechanism | Who talks | Frequency |
|---|---|---|---|
| "Is the app alive?" | **UDP broadcast heartbeat** | the app emits | every 15 s |
| "What is its detailed state?" | **HTTP `/status` server** | the supervisor asks | on demand |

The supervisor scans nothing: it **listens** passively. No IP to know, no
configuration, automatic discovery. An app that stops emitting for ~1 minute is
considered offline. Detailed metrics **never** travel in the heartbeat: they stay
behind `/status`, queried only when needed.

## The `morfbeacon/1` protocol

**UDP heartbeat** (compact JSON, broadcast on port `45454`):

```json
{
  "proto": "morfbeacon/1",
  "app": "ComponentHub",
  "host": "fredpc",
  "version": "1.6.0",
  "state": "ok",
  "status_port": 8787,
  "instance": "ComponentHub@fredpc",
  "uptime_s": 3600,
  "ts": 1752400000
}
```

**HTTP `GET /status`** (on `status_port`):

```json
{
  "app": "ComponentHub",
  "host": "fredpc",
  "version": "1.6.0",
  "state": "ok",
  "uptime_s": 3600,
  "metrics": { "components": 812, "projects": 14, "last_backup_age_s": 7200 },
  "ts": 1752400000
}
```

`GET /healthz` returns `{"status":"ok"}` (a lightweight liveness probe). The full
protocol is specified in [docs/fr/PROTOCOL.md](docs/fr/PROTOCOL.md) *(FR)*.

### Declaring a web interface

An application that serves a web interface declares it by setting one field:

```cpp
cfg.webUiPath        = "/";                       // the whole declaration
cfg.webUiLabel       = "Analyses météo";          // optional, defaults to appName
cfg.webUiDescription = "Tendances et corrélations."; // optional
// cfg.webUiPort     = 8080;                      // optional, defaults to statusPort
```

The capability `web_ui` is then **added automatically** to the heartbeat, and the
detail appears in `/status`:

```json
"capabilities": ["web_ui"],
```

```json
"web_ui": { "path": "/", "label": "Analyses météo", "port": 8799 }
```

A consumer discovers the service, sees the capability, fetches `/status` **once**
to learn how to open it, and offers a link — **without knowing the application**.
Adding a new service to the ecosystem therefore requires no change to any
consumer.

The capability is derived from `webUiPath`, never declared separately: the
detail and the capability that makes it discoverable cannot drift apart.

## Integration in 5 lines

```cpp
#include <morfbeacon/PresenceService.h>
#include <morfbeacon/IMetricsProvider.h>

morfbeacon::PresenceConfig cfg;
cfg.appName = "ComponentHub";
cfg.version = APP_VERSION;

morfbeacon::FunctionMetricsProvider provider([this] {
    QJsonObject m;
    m["components"] = m_inventory->count();
    return m;
});

auto* presence = new morfbeacon::PresenceService(cfg, &provider, this);
presence->start();
```

Detailed guide (CMake + where to wire the code in ComponentHub / SiteWatch):
**[docs/fr/INTEGRATION.md](docs/fr/INTEGRATION.md)** *(FR)*.

## Building

Same commands as ComponentHub / SiteWatch:

```sh
# Windows (MSYS2 / MinGW)
cmake --preset mingw
cmake --build --preset mingw

# Linux / Raspberry Pi
cmake --preset linux          # or linux-arm64
cmake --build --preset linux
```

In a standalone build, the `morfbeacon_demo` example is compiled
(`build-*/examples/minimal/`).

## Try it without hardware

In two terminals:

```sh
# 1. the "fake app" (emits the heartbeat + exposes /status)
./build-mingw/examples/minimal/morfbeacon_demo

# 2. the "fake dashboard" (listens + polls), no dependency
python tools/fake_dashboard.py --poll --every 10
```

The tester shows discovery, offline transitions and metrics. It reproduces
exactly what RaspberryDashboard does.

## Dependencies

Qt 6 (**Core** + **Network** only — no Widgets, usable in a headless service).
C++17, CMake ≥ 3.21.

## Documentation

The in-depth guides are in **French** under [`docs/fr/`](docs/fr/README.md); an
English index is at [`docs/en/`](docs/en/README.md).

| Document | Contents |
|---|---|
| [docs/fr/PROTOCOL.md](docs/fr/PROTOCOL.md) *(FR)* | The `morfbeacon/1` wire protocol (heartbeat, `/status`, ports) |
| [docs/fr/ARCHITECTURE.md](docs/fr/ARCHITECTURE.md) *(FR)* | The classes (Heartbeat, StatusServer, providers, PresenceService) |
| [docs/fr/INTEGRATION.md](docs/fr/INTEGRATION.md) *(FR)* | Integrating morfBeacon into an application |
| [CHANGELOG.md](CHANGELOG.md) | Version history |
| [ROADMAP.md](ROADMAP.md) | Planned work |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Contribution guide |

## License

Distributed under the [GPL-3.0-only license](LICENSE). © 2026 morfredus.
