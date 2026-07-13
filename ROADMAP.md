# Roadmap

## Done

- **v0.1.0** — UDP heartbeat presence + HTTP `/status` endpoint + metrics
  provider interface + `fake_dashboard.py` tester. Integrated into ComponentHub
  and SiteWatch; consumed by RaspberryDashboard.

## Planned

- **State-change signals** — emit a Qt signal when `state()` changes, for
  reactive supervisors.
- **Optional authentication** on `/status` (shared token) for untrusted networks.
- **Headless configuration** — load `PresenceConfig` from a file / environment
  for services without a GUI.
- **IPv6 / multicast** option alongside IPv4 broadcast.
- **English translation** of the `docs/fr/` guides under `docs/en/`.
