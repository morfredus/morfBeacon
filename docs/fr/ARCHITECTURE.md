# Architecture — morfBeacon

Retour à l'[index de la documentation](README.md).

---

morfBeacon est une petite bibliothèque **Qt (Core + Network)**, sans Widgets,
donc utilisable dans une application graphique comme dans un service sans
interface. Elle est volontairement minimale : cinq pièces.

## Les pièces

```
PresenceService  (façade : câble les deux canaux)
├── Heartbeat     -> émission UDP (présence)          [QUdpSocket + QTimer]
└── StatusServer  -> endpoint HTTP /status (détail)   [QTcpServer]
        ▲
        │ interroge
IMetricsProvider  (point d'extension fourni par l'application)
```

### `PresenceConfig` (struct)

Les paramètres : `appName`, `version`, `instanceId` (optionnel), `udpPort`
(45454), `broadcastIntervalMs` (15000), `statusPort`, `statusBindAddress`. La
constante `kProto` porte la version du protocole (`morfbeacon/1`).

### `IMetricsProvider` (interface)

Le **seul** point d'extension. L'application l'implémente pour fournir :

- `metrics()` → un `QJsonObject` libre (exposé **uniquement** via `/status`) ;
- `state()` → `"ok" | "warning" | "error" | "starting"` (dans le heartbeat ET
  `/status`).

`FunctionMetricsProvider` en fournit une implémentation prête à l'emploi à partir
de lambdas, pour intégrer sans créer de sous-classe.

### `Heartbeat` (QObject)

Émet le datagramme UDP périodique. Construit le JSON (proto, app, host, version,
state, status_port, instance, uptime_s, ts) et l'envoie en broadcast sur chaque
interface active. Ne contient **aucune** métrique détaillée.

### `StatusServer` (QObject)

Minuscule serveur HTTP/1.1 sur `QTcpServer`. Sert `/status` (JSON complet avec
`metrics`) et `/healthz`. Une requête, une réponse, connexion fermée. Parsing
volontairement minimal (une requête `GET` est minuscule), avec un garde-fou de
taille.

### `PresenceService` (façade)

L'unique objet que l'application manipule. Il crée le `Heartbeat` et le
`StatusServer` à partir d'un `PresenceConfig` + un `IMetricsProvider`, et aligne
le `status_port` annoncé sur le port réellement ouvert (annonce `0` si le serveur
HTTP n'a pas pu démarrer).

## Fil d'exécution

Tout tourne sur **le thread principal Qt** (boucle d'événements). Le
`IMetricsProvider::metrics()` est appelé au moment d'une requête `/status`, donc
sur ce thread : pas de synchronisation à prévoir tant que les données lues
vivent sur le thread UI. Pour des métriques coûteuses, les pré-calculer ailleurs
et n'exposer qu'un instantané.

## Portabilité

Aucun code spécifique à une plateforme ni à une architecture : `QUdpSocket`,
`QTcpServer`, `QNetworkInterface`, `QHostInfo` sont multiplateformes. Le
comportement est identique sous Windows, Linux x64 et Raspberry Pi (ARM64) — Qt
active notamment `SO_BROADCAST` de lui-même.
