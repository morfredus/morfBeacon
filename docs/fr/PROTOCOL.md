# Protocole `morfbeacon/1`

Retour à l'[index de la documentation](README.md).

---

morfBeacon repose sur **deux canaux aux rôles bien séparés** : un heartbeat UDP
pour la **présence**, un endpoint HTTP pour le **détail**. Ce document spécifie
le format de chacun, pour qu'un superviseur (RaspberryDashboard, ou tout autre)
puisse l'implémenter sans dépendre de la bibliothèque.

## 1. Heartbeat UDP (présence)

- **Transport** : UDP, datagramme unique, **broadcast** sur le réseau local.
- **Port** : `45454` (commun à tout le parc).
- **Périodicité** : toutes les 15 s par défaut (`broadcastIntervalMs`).
- **Émission** : sur l'adresse de broadcast de **chaque interface active** (plus
  fiable qu'un broadcast global sur une machine multi-réseaux) ; repli sur
  `255.255.255.255` si aucune interface exploitable.
- **Charge utile** : un objet JSON compact (une seule ligne).

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

| Champ | Type | Description |
|---|---|---|
| `proto` | string | Version du protocole. Toujours `morfbeacon/<n>`. **Ignorer** un datagramme dont le préfixe n'est pas `morfbeacon/`. |
| `app` | string | Nom de l'application (identifiant logique). |
| `host` | string | Nom d'hôte de la machine. |
| `version` | string | Version de l'application. |
| `state` | string | État de santé : `ok`, `warning`, `error`, `starting`. |
| `status_port` | number | Port HTTP du endpoint `/status` (0 = pas de serveur HTTP). |
| `instance` | string | Identité stable `app@host` (permet plusieurs instances). |
| `uptime_s` | number | Secondes depuis le démarrage du service de présence. |
| `ts` | number | Horodatage Unix (secondes) de l'émission. |

**Côté superviseur** : écouter le port `45454`, tenir à jour la date du dernier
heartbeat par `instance` (ou `app`). Une application **sans heartbeat depuis
~60 s** est considérée **hors ligne**. Aucune sonde, aucune IP à connaître :
l'adresse source du datagramme donne l'IP pour joindre `/status`.

## 2. HTTP `/status` (détail, à la demande)

Petit serveur HTTP/1.1 exposé par l'application sur `status_port`. Interrogé
**seulement quand c'est utile** (ouverture d'une fiche, ou basse fréquence).

**`GET /status`** →

```json
{
  "app": "ComponentHub",
  "host": "fredpc",
  "version": "1.6.0",
  "state": "ok",
  "uptime_s": 3600,
  "metrics": { "components": 812, "projects": 14 },
  "ts": 1752400000
}
```

- `metrics` : objet **libre**, propre à l'application (compteurs, files, etc.).
  Le superviseur l'affiche sans en connaître la structure.
- Réponse : `Content-Type: application/json`, en-tête `Access-Control-Allow-Origin: *`
  (pour un futur tableau de bord web), `Connection: close`.

**`GET /healthz`** → `{"status":"ok"}` — sonde de vie légère.

Toute autre route → `404`. Toute méthode autre que `GET` → `405`.

## 3. Convention de ports

- **UDP `45454`** : identique pour **toutes** les applications (canal d'annonce).
- **HTTP `status_port`** : **un port distinct par application** sur une même
  machine.

  | Application | status_port |
  |---|---|
  | ComponentHub | 8787 |
  | SiteWatch | 8788 |
  | GatewayLab | 8789 |

## 4. Versionnage du protocole

Le champ `proto` porte la version. Un changement **incompatible** du format du
heartbeat incrémente le numéro (`morfbeacon/2`). Les superviseurs doivent
**ignorer** les protocoles qu'ils ne comprennent pas plutôt que de planter.
