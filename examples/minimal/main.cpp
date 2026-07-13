/*
 * morfBeacon — exemple de demonstration
 * Copyright (C) 2026 morfredus
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Simule une application supervisee : emet un heartbeat UDP et expose /status.
 * A lancer en parallele de tools/fake_dashboard.py pour voir la decouverte.
 */

#include <QCoreApplication>
#include <QJsonObject>
#include <QDateTime>

#include <morfbeacon/PresenceService.h>
#include <morfbeacon/IMetricsProvider.h>

int main(int argc, char** argv) {
    QCoreApplication app(argc, argv);

    morfbeacon::PresenceConfig cfg;
    cfg.appName = QStringLiteral("DemoApp");
    cfg.version = QStringLiteral(MORFBEACON_VERSION);
    cfg.statusPort = 8787;
    cfg.broadcastIntervalMs = 5000; // 5 s pour une demo reactive

    // Metriques factices, recalculees a chaque appel de /status.
    int scans = 0;
    morfbeacon::FunctionMetricsProvider provider(
        [&scans]() {
            QJsonObject m;
            m["scans_total"]      = ++scans;
            m["queue_size"]       = scans % 4;
            m["devices_found"]    = 7;
            return m;
        },
        []() { return QStringLiteral("ok"); });

    morfbeacon::PresenceService presence(cfg, &provider);
    if (!presence.start())
        qWarning("Serveur /status non demarre (port %u occupe ?)", cfg.statusPort);

    qInfo("morfBeacon demo : heartbeat UDP toutes les %d ms sur le port %u ; "
          "GET http://localhost:%u/status",
          cfg.broadcastIntervalMs, cfg.udpPort, cfg.statusPort);

    return app.exec();
}
