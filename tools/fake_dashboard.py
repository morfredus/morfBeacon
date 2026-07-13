#!/usr/bin/env python3
"""
fake_dashboard.py — testeur de morfBeacon cote superviseur.

Reproduit ce que fera RaspberryDashboard, sans dependance externe (stdlib
uniquement) :

  1. ECOUTE le heartbeat UDP en broadcast (port 45454) et tient a jour la liste
     des applications vues, avec passage OFFLINE apres un delai sans annonce.
  2. INTERROGE l'endpoint HTTP /status a la demande (option --poll) pour
     afficher les metriques detaillees.

Usage :
    python fake_dashboard.py                 # ecoute seule, tableau de presence
    python fake_dashboard.py --poll          # + interroge /status toutes les 60 s
    python fake_dashboard.py --poll --every 10
    python fake_dashboard.py --port 45454

Ctrl+C pour quitter.
"""

import argparse
import json
import socket
import sys
import threading
import time
import urllib.request
from datetime import datetime

UDP_PORT = 45454          # doit correspondre a PresenceConfig::udpPort
OFFLINE_AFTER = 60.0      # secondes sans heartbeat avant de declarer OFFLINE

# instance -> dernier etat connu
_seen = {}
_lock = threading.Lock()


def _now():
    return datetime.now().strftime("%H:%M:%S")


def listen_udp(port):
    """Boucle d'ecoute des heartbeats UDP broadcast."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    except (AttributeError, OSError):
        pass  # SO_REUSEPORT indisponible sous Windows
    sock.bind(("", port))
    print(f"[{_now()}] Ecoute des heartbeats UDP sur le port {port}...\n")

    while True:
        data, addr = sock.recvfrom(2048)
        try:
            msg = json.loads(data.decode("utf-8"))
        except (ValueError, UnicodeDecodeError):
            continue
        if not str(msg.get("proto", "")).startswith("morfbeacon/"):
            continue

        instance = msg.get("instance") or f"{msg.get('app')}@{addr[0]}"
        with _lock:
            first_seen = instance not in _seen
            _seen[instance] = {
                "app": msg.get("app", "?"),
                "host": msg.get("host", "?"),
                "version": msg.get("version", "?"),
                "state": msg.get("state", "?"),
                "ip": addr[0],
                "status_port": int(msg.get("status_port", 0) or 0),
                "last_seen": time.monotonic(),
                "online": True,
            }
        if first_seen:
            e = _seen[instance]
            print(f"[{_now()}] DECOUVERT  {instance}  "
                  f"({e['app']} v{e['version']} @ {e['ip']}, "
                  f"status_port={e['status_port']}, etat={e['state']})")


def watch_offline():
    """Passe une instance OFFLINE si aucun heartbeat depuis OFFLINE_AFTER."""
    while True:
        time.sleep(5)
        now = time.monotonic()
        with _lock:
            for instance, e in _seen.items():
                if e["online"] and (now - e["last_seen"]) > OFFLINE_AFTER:
                    e["online"] = False
                    print(f"[{_now()}] OFFLINE    {instance} "
                          f"(aucun heartbeat depuis {OFFLINE_AFTER:.0f} s)")


def fetch_status(ip, port, timeout=2.0):
    url = f"http://{ip}:{port}/status"
    with urllib.request.urlopen(url, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def poll_loop(every):
    """Interroge /status de chaque application en ligne, periodiquement."""
    while True:
        time.sleep(every)
        with _lock:
            targets = [
                (inst, e["ip"], e["status_port"])
                for inst, e in _seen.items()
                if e["online"] and e["status_port"]
            ]
        for inst, ip, port in targets:
            try:
                status = fetch_status(ip, port)
                metrics = status.get("metrics", {})
                metrics_txt = ", ".join(f"{k}={v}" for k, v in metrics.items())
                print(f"[{_now()}] /status    {inst}  "
                      f"etat={status.get('state')} uptime={status.get('uptime_s')}s"
                      f"  [{metrics_txt}]")
            except (OSError, ValueError) as exc:
                print(f"[{_now()}] /status    {inst}  ECHEC ({exc})")


def main():
    ap = argparse.ArgumentParser(description="Testeur superviseur pour morfBeacon")
    ap.add_argument("--port", type=int, default=UDP_PORT,
                    help=f"port UDP du heartbeat (defaut {UDP_PORT})")
    ap.add_argument("--poll", action="store_true",
                    help="interroger aussi l'endpoint HTTP /status")
    ap.add_argument("--every", type=float, default=60.0,
                    help="periode d'interrogation /status en secondes (defaut 60)")
    args = ap.parse_args()

    threading.Thread(target=watch_offline, daemon=True).start()
    if args.poll:
        threading.Thread(target=poll_loop, args=(args.every,), daemon=True).start()

    try:
        listen_udp(args.port)
    except KeyboardInterrupt:
        print("\nArret.")
        sys.exit(0)


if __name__ == "__main__":
    main()
