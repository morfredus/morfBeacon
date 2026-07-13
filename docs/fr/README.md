# Documentation de morfBeacon (français)

Bibliothèque C++ commune de supervision LAN (heartbeat UDP + endpoint HTTP
`/status`) pour les applications de bureau.

> 🇬🇧 English documentation: [`docs/en/`](../en/README.md) *(index, in progress)*.
> Retour au [README (français)](../../README.fr.md).

## Comprendre et intégrer

| Document | Contenu |
|---|---|
| [Protocole `morfbeacon/1`](PROTOCOL.md) | Le format sur le fil (heartbeat UDP, `/status`, `/healthz`, ports) — pour implémenter un superviseur. |
| [Architecture](ARCHITECTURE.md) | Les classes (Heartbeat, StatusServer, IMetricsProvider, PresenceService) et le fil d'exécution. |
| [Intégration](INTEGRATION.md) | Brancher morfBeacon dans une application Qt (CMake + code). |

## À la racine du projet

| Document | Contenu |
|---|---|
| [README](../../README.md) | Présentation générale (anglais). |
| [README (français)](../../README.fr.md) | Présentation générale (français). |
| [Journal des versions](../../CHANGELOG.md) | Historique des versions. |
| [Roadmap](../../ROADMAP.md) | Évolutions envisagées. |
| [Contribuer](../../CONTRIBUTING.md) | Guide de contribution. |
