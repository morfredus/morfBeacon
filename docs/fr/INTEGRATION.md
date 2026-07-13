# Intégrer morfBeacon dans une application

Ce guide montre comment brancher morfBeacon dans **ComponentHub** et **SiteWatch**.
La démarche est identique pour toute future application Qt.

## 1. Récupérer la bibliothèque

Deux options.

### a) En sous-module / dossier voisin (recommandé pour commencer)

Place `morfBeacon_travail/` à côté du projet, puis dans le `CMakeLists.txt` de
l'application :

```cmake
add_subdirectory(../morfBeacon_travail morfBeacon EXTERNAL_SOURCE)
# ...
target_link_libraries(ComponentHub PRIVATE morfBeacon::morfBeacon)
```

> `EXTERNAL_SOURCE` est un nom de dossier de build arbitraire, requis car la
> source est hors de l'arborescence du projet.

### b) En copie interne

Copie `morfBeacon_travail/` dans `third_party/morfBeacon/` du projet, puis :

```cmake
add_subdirectory(third_party/morfBeacon)
target_link_libraries(ComponentHub PRIVATE morfBeacon::morfBeacon)
```

Dans les deux cas, l'exemple de démo n'est **pas** compilé (il ne l'est qu'en
build autonome de morfBeacon).

## 2. Fournir les métriques de l'application

Le seul travail spécifique à l'appli : décrire ce qu'elle expose. Deux façons.

### Simple — une lambda (`FunctionMetricsProvider`)

```cpp
#include <morfbeacon/IMetricsProvider.h>

morfbeacon::FunctionMetricsProvider provider(
    [this]() {
        QJsonObject m;
        m["components"] = m_inventoryService->count();
        m["projects"]   = m_projectService->count();
        return m;
    },
    [this]() -> QString {
        return m_lastBackupOk ? "ok" : "warning";
    });
```

### Structuré — une sous-classe (`IMetricsProvider`)

Pratique si la collecte est plus riche (à ranger dans `src/platform/` pour
ComponentHub, `src/core/` pour SiteWatch — la couche qui ne dépend pas de l'UI) :

```cpp
class AppMetrics : public morfbeacon::IMetricsProvider {
public:
    explicit AppMetrics(AppContext* ctx) : m_ctx(ctx) {}
    QJsonObject metrics() const override {
        QJsonObject m;
        m["components"] = m_ctx->inventory().count();
        return m;
    }
    QString state() const override {
        return m_ctx->hasErrors() ? "error" : "ok";
    }
private:
    AppContext* m_ctx;
};
```

## 3. Démarrer le service

Dans le constructeur de `MainWindow` (ou juste après la création de
l'`AppContext`), une fois les services métier prêts :

```cpp
#include <morfbeacon/PresenceService.h>

morfbeacon::PresenceConfig cfg;
cfg.appName    = "ComponentHub";      // ou "SiteWatch"
cfg.version    = COMPONENTHUB_VERSION; // la macro deja definie par CMake
cfg.statusPort = 8787;                 // choisir un port par appli (voir plus bas)

// 'm_metricsProvider' et 'm_presence' sont des membres pour rester en vie.
m_presence = new morfbeacon::PresenceService(cfg, m_metricsProvider, this);
m_presence->start();
```

`PresenceService` a `this` (le QObject parent) pour parent : il est détruit
automatiquement avec la fenêtre. Rien à faire à la fermeture.

## 4. Choisir les ports

- **UDP `45454`** : identique pour **toutes** les applis (c'est le canal commun
  d'annonce). Ne pas changer, sauf pour isoler un réseau.
- **HTTP `status_port`** : **un port distinct par application** sur une même
  machine, sinon la seconde ne pourra pas ouvrir le sien. Convention proposée :

  | Application   | status_port |
  |---------------|-------------|
  | ComponentHub  | 8787        |
  | SiteWatch     | 8788        |
  | GatewayLab    | 8789        |

  Le heartbeat annonce le port réellement ouvert ; si le port est occupé,
  `start()` renvoie `false` et l'appli reste tout de même annoncée (sans détail).

## 5. Rappel des versions déjà disponibles

Les deux projets définissent déjà leur version via CMake :

- ComponentHub : ajouter `target_compile_definitions(... COMPONENTHUB_VERSION="${PROJECT_VERSION}")`
  s'il n'existe pas encore (SiteWatch a déjà `SITEWATCH_VERSION`).
- Utiliser cette macro pour `cfg.version`, afin que la version annoncée suive
  toujours le fichier `VERSION`.

## 6. Vérifier

Lancer l'application, puis dans un terminal :

```sh
python morfBeacon_travail/tools/fake_dashboard.py --poll --every 10
```

Tu dois voir `DECOUVERT ComponentHub@...` en quelques secondes, puis les
métriques via `/status`. Tu peux aussi tester l'endpoint directement :

```sh
curl http://localhost:8787/status
```

## Côté RaspberryDashboard (plus tard)

Le dashboard passera de **sonde active** (`NETWORK_SERVICES` qui fait un
`socket.create_connection` vers `componenthub.local:80`) à **écoute passive** du
heartbeat, exactement comme `tools/fake_dashboard.py`. La logique d'écoute UDP +
interrogation `/status` de ce script est directement réutilisable dans un module
`presence.py`. Aucune modification ne sera nécessaire côté applications quand un
nouvel outil rejoindra le parc : il suffira qu'il intègre morfBeacon.
