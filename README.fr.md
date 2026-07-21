# morfBeacon

*Lire dans une autre langue : [English](README.md) · **Français** (ce document).*

[![Version](https://img.shields.io/badge/version-0.4.0-blue)](CHANGELOG.md)
![C++](https://img.shields.io/badge/C%2B%2B-17-00599C?logo=cplusplus)
![Qt](https://img.shields.io/badge/Qt-6-41CD52?logo=qt)
![Build](https://img.shields.io/badge/CMake-3.21+-064F8C?logo=cmake)
![Licence](https://img.shields.io/badge/Licence-GPL--3.0--only-blue)

**Bibliothèque C++ commune de supervision LAN pour les applications de bureau.**

morfBeacon permet à une application (ComponentHub, SiteWatch, GatewayLab, et les
outils à venir) d'**annoncer sa présence** sur le réseau local et d'**exposer ses
métriques** à un superviseur (RaspberryDashboard), en quelques lignes de code.

## Principe : *push présence / pull détail*

Deux besoins bien distincts, deux mécanismes :

| Besoin | Mécanisme | Qui parle | Fréquence |
|---|---|---|---|
| « Est-ce que l'appli est en vie ? » | **Heartbeat UDP broadcast** | l'appli émet | toutes les 15 s |
| « Quel est son état détaillé ? » | **Serveur HTTP `/status`** | le superviseur interroge | à la demande |

Le superviseur ne scanne rien : il **écoute** passivement. Aucune IP à connaître,
aucune configuration, découverte automatique. Une appli qui n'émet plus pendant
~1 minute est considérée hors ligne. Les métriques détaillées ne transitent
**jamais** par le heartbeat : elles restent derrière `/status`, interrogé
seulement quand on en a besoin.

## Le protocole `morfbeacon/1`

**Heartbeat UDP** (JSON compact, broadcast sur le port `45454`) :

```json
{
  "proto": "morfbeacon/1",
  "app": "ComponentHub",
  "host": "fredpc",
  "version": "1.6.0",
  "state": "ok",
  "status_port": 8787,
  "instance": "ComponentHub@fredpc",
  "capabilities": ["storage"],
  "uptime_s": 3600,
  "ts": 1752400000
}
```

**HTTP `GET /status`** (sur `status_port`) :

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

`GET /healthz` renvoie `{"status":"ok"}` (sonde de vie légère). Le protocole
complet est spécifié dans [docs/fr/PROTOCOL.md](docs/fr/PROTOCOL.md).

## Intégration en 5 lignes

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

Guide détaillé (CMake + où brancher le code dans ComponentHub / SiteWatch) :
**[docs/fr/INTEGRATION.md](docs/fr/INTEGRATION.md)**.

## Compilation

Mêmes commandes que ComponentHub / SiteWatch :

```sh
# Windows (MSYS2 / MinGW)
cmake --preset mingw
cmake --build --preset mingw

# Linux / Raspberry Pi
cmake --preset linux          # ou linux-arm64
cmake --build --preset linux
```

En build autonome, l'exemple `morfbeacon_demo` est compilé (`build-*/examples/minimal/`).

## Essayer sans matériel

Dans deux terminaux :

```sh
# 1. la « fausse appli » (émet le heartbeat + expose /status)
./build-mingw/examples/minimal/morfbeacon_demo

# 2. le « faux dashboard » (écoute + interroge), sans dépendance
python tools/fake_dashboard.py --poll --every 10
```

Le testeur affiche la découverte, les passages hors ligne et les métriques.
Il reproduit exactement ce que fait RaspberryDashboard.

## Dépendances

Qt 6 (**Core** + **Network** uniquement — pas de Widgets, utilisable dans un
service sans interface). C++17, CMake ≥ 3.21.

## Documentation

-   [docs/fr/PROTOCOL.md](docs/fr/PROTOCOL.md) — le protocole `morfbeacon/1` (heartbeat, `/status`, ports)
-   [docs/fr/ARCHITECTURE.md](docs/fr/ARCHITECTURE.md) — les classes (Heartbeat, StatusServer, fournisseurs, PresenceService)
-   [docs/fr/INTEGRATION.md](docs/fr/INTEGRATION.md) — intégrer morfBeacon dans une application
-   [CHANGELOG.md](CHANGELOG.md) — historique des versions
-   [ROADMAP.md](ROADMAP.md) — évolutions prévues
-   [CONTRIBUTING.md](CONTRIBUTING.md) — guide de contribution

> Index : [`docs/fr/`](docs/fr/README.md) (français) · [`docs/en/`](docs/en/README.md) (anglais).

## Licence

Distribué sous la licence [GPL-3.0-only](LICENSE). © 2026 morfredus.
