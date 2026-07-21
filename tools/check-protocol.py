#!/usr/bin/env python3
"""
check-protocol.py — verifie que le protocole morfbeacon/1 est respecte.

Pourquoi cet outil existe
-------------------------
Le protocole a maintenant CINQ implementations, imposees par les frontieres de
plateforme et de langage :

    emetteurs   Heartbeat.cpp (Qt)            arduino/morfbeacon_emitter.h (ESP32)
    ecouteurs   MonitorModule.cpp (Qt)        analytics_beacon.cpp (ESP32)
                beacon_listener.py (Python)

Aucune ne peut etre partagee avec les autres. Ce qui est commun n'est donc pas
du code mais un FORMAT, et un format sans verification derive en silence : un
champ renomme, un entier passe en chaine, une capacite mal orthographiee, et un
consommateur cesse de voir un service sans que rien ne le signale.

Ce script est la reference executable de ce format. Lance sur le reseau local,
il valide les datagrammes REELS de toutes les implementations a la fois — c'est
le seul point d'ou l'on voit les cinq en meme temps.

Il ne modifie rien et n'emet rien : il ecoute, constate, explique.

Usage :
    check-protocol.py                    # ecoute 20 s, valide tout ce qui passe
    check-protocol.py --seconds 60       # ecoute plus longtemps
    check-protocol.py --no-pull          # ne pas interroger les /status
    check-protocol.py --file capture.json  # valider un datagramme enregistre

Code de retour : 0 si tout est conforme, 1 sinon.
"""

import argparse
import json
import socket
import sys
import urllib.error
import urllib.request

PROTO = "morfbeacon/1"
PORT = 45454

OK, ERR, WARN, INFO = "[OK]", "[ERREUR]", "[ATTENTION]", "[INFO]"


# --------------------------------------------------------------------------
# Le contrat
# --------------------------------------------------------------------------

def check_heartbeat(o):
    """Valide un datagramme. Renvoie (erreurs, avertissements)."""
    err, warn = [], []

    def need(key, kind, label):
        if key not in o:
            err.append(f"champ obligatoire absent : {key}")
            return None
        if not isinstance(o[key], kind):
            err.append(f"{key} : attendu {label}, recu {type(o[key]).__name__}")
            return None
        return o[key]

    proto = need("proto", str, "chaine")
    if proto is not None and proto != PROTO:
        err.append(f"proto vaut '{proto}', attendu '{PROTO}'")

    for key in ("app", "host", "version", "state", "instance"):
        value = need(key, str, "chaine")
        if value is not None and not value.strip():
            err.append(f"{key} est vide")

    port = need("status_port", int, "entier")
    if port is not None and not (0 <= port <= 65535):
        err.append(f"status_port hors plage : {port}")

    uptime = need("uptime_s", int, "entier")
    if uptime is not None and uptime < 0:
        err.append(f"uptime_s negatif : {uptime}")

    # ts : 0 est LEGITIME. Un ESP32 sans NTP n'a pas d'horloge, et emettre 0
    # — lisible comme « inconnu » — vaut mieux qu'une date de 1970 qu'un
    # consommateur prendrait pour une mesure.
    ts = need("ts", int, "entier")
    if ts is not None and ts != 0 and ts < 1_600_000_000:
        warn.append(f"ts={ts} : ni 0 ni une date plausible (horloge non reglee ?)")

    # capabilities est FACULTATIF : un service qui n'en declare aucune ne doit
    # pas emettre le champ, pour que le datagramme reste court.
    caps = o.get("capabilities")
    if caps is not None:
        if not isinstance(caps, list):
            err.append("capabilities : attendu une liste")
        else:
            for c in caps:
                if not isinstance(c, str):
                    err.append(f"capabilities contient un non-texte : {c!r}")
                elif c != c.lower() or " " in c or "-" in c:
                    # Une capacite est un identifiant stable, en minuscules avec
                    # tirets bas. Une variante d'orthographe rend le service
                    # invisible au consommateur qui cherche la bonne.
                    err.append(f"capacite mal formee : '{c}' "
                               "(minuscules et tirets bas attendus)")

    if len(json.dumps(o, separators=(",", ":"))) > 512:
        warn.append("datagramme > 512 octets : le heartbeat doit rester court, "
                    "le detail vit derriere /status")

    return err, warn


def check_status(o, declares_web_ui):
    """Valide un document /status. `declares_web_ui` vient du heartbeat."""
    err, warn = [], []

    for key in ("app", "host", "version", "state"):
        if key not in o:
            err.append(f"champ obligatoire absent : {key}")
        elif not isinstance(o[key], str):
            err.append(f"{key} : attendu une chaine")

    if "uptime_s" in o and not isinstance(o["uptime_s"], int):
        err.append("uptime_s : attendu un entier")
    if "metrics" in o and not isinstance(o["metrics"], dict):
        err.append("metrics : attendu un objet")

    ui = o.get("web_ui")

    # LA verification qui compte. Le heartbeat annonce une capacite, /status en
    # donne le moyen d'ouverture : declarer l'une sans servir l'autre produit une
    # interface que personne ne saura ouvrir. Ce defaut s'est produit deux fois
    # dans l'ecosysteme (morfMonitor 0.3.1, puis evite de justesse dans
    # morfAnalytics), toujours parce que le service reimplemente son propre
    # /status et oublie ce bloc.
    if declares_web_ui and ui is None:
        err.append("le heartbeat annonce la capacite 'web_ui' mais /status ne "
                   "publie aucun bloc web_ui : l'interface est indecouvrable")
    if ui is not None and not declares_web_ui:
        warn.append("/status publie web_ui alors que le heartbeat n'annonce pas "
                    "la capacite : un consommateur ne saura pas qu'il faut regarder")

    if isinstance(ui, dict):
        path = ui.get("path")
        if not isinstance(path, str) or not path.startswith("/"):
            err.append(f"web_ui.path invalide : {path!r} (chemin absolu attendu)")
        if not isinstance(ui.get("label"), str) or not ui.get("label", "").strip():
            err.append("web_ui.label absent ou vide")
        port = ui.get("port")
        if not isinstance(port, int) or not (1 <= port <= 65535):
            err.append(f"web_ui.port invalide : {port!r}")
    elif ui is not None:
        err.append("web_ui : attendu un objet")

    return err, warn


# --------------------------------------------------------------------------

def report(label, err, warn):
    for e in err:
        print(f"  {ERR} {e}")
    for w in warn:
        print(f"  {WARN} {w}")
    if not err and not warn:
        print(f"  {OK} conforme")
    return len(err)


def fetch_status(ip, port, timeout=3.0):
    url = f"http://{ip}:{port}/status"
    try:
        with urllib.request.urlopen(url, timeout=timeout) as r:
            return json.loads(r.read()), None
    except (urllib.error.URLError, OSError, ValueError, TimeoutError) as exc:
        return None, str(exc)


def listen(seconds, pull):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        sock.bind(("", PORT))
    except OSError as exc:
        print(f"{ERR} impossible d'ecouter sur le port {PORT} : {exc}")
        return 2
    sock.settimeout(1.0)

    print(f"Ecoute du port {PORT} pendant {seconds} s...\n")
    seen = {}          # app -> (objet, ip)
    malformed = 0
    import time
    deadline = time.time() + seconds
    while time.time() < deadline:
        try:
            data, addr = sock.recvfrom(4096)
        except socket.timeout:
            continue
        try:
            o = json.loads(data)
        except ValueError:
            malformed += 1
            continue
        if not isinstance(o, dict) or o.get("proto") != PROTO:
            continue
        seen[o.get("app", "?")] = (o, addr[0])

    if malformed:
        print(f"{WARN} {malformed} datagramme(s) illisible(s) ignore(s) sur ce port.\n")

    if not seen:
        print(f"{ERR} aucun emetteur entendu.")
        print("        Verifier que des services tournent, et que la diffusion UDP")
        print("        n'est pas filtree entre cette machine et eux.")
        return 1

    failures = 0
    for app, (o, ip) in sorted(seen.items()):
        print(f"--- {app}  ({ip}, v{o.get('version', '?')}) ---")
        err, warn = check_heartbeat(o)
        failures += report("heartbeat", err, warn)

        caps = o.get("capabilities") or []
        declares = "web_ui" in caps
        port = o.get("status_port")

        if pull and isinstance(port, int) and port > 0:
            status, error = fetch_status(ip, port)
            if status is None:
                # Un /status injoignable n'est un manquement que si une capacite
                # a ete annoncee : sans cela, le service n'a rien promis.
                level = ERR if declares else INFO
                print(f"  {level} /status injoignable ({error})")
                if declares:
                    failures += 1
            else:
                print(f"  {INFO} /status interroge")
                serr, swarn = check_status(status, declares)
                failures += report("status", serr, swarn)
        print()

    print(f"{len(seen)} emetteur(s) verifie(s).")
    return 1 if failures else 0


def main():
    ap = argparse.ArgumentParser(add_help=True, description=__doc__.split("\n")[1])
    ap.add_argument("--seconds", type=int, default=20,
                    help="duree d'ecoute (defaut : 20, > un intervalle de 15 s)")
    ap.add_argument("--no-pull", action="store_true",
                    help="ne pas interroger les /status des services entendus")
    ap.add_argument("--file", help="valider un datagramme enregistre au lieu d'ecouter")
    args = ap.parse_args()

    if args.file:
        try:
            with open(args.file, encoding="utf-8-sig") as fh:
                o = json.load(fh)
        except (OSError, ValueError) as exc:
            print(f"{ERR} fichier illisible : {exc}")
            return 2
        print(f"--- {args.file} ---")
        return 1 if report("heartbeat", *check_heartbeat(o)) else 0

    return listen(args.seconds, not args.no_pull)


if __name__ == "__main__":
    sys.exit(main())
