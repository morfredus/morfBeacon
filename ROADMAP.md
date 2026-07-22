# Roadmap

## Done

- **v0.3.0** — `web_ui` capability: a service declares its web interface with a
  single field, the capability travels in the heartbeat and the detail behind
  `/status`. A consumer can offer a link without knowing the application.
- **v0.2.0** — `capabilities` field: consumers match on what a service *can do*,
  not on what it is *called* — names are user-modifiable under the GPL.
- **v0.1.0** — UDP heartbeat presence + HTTP `/status` endpoint + metrics
  provider interface + `fake_dashboard.py` tester. Integrated into ComponentHub
  and SiteWatch; consumed by morfDashboard.

## Planned

- **Emitter for embedded targets (ESP32)** — the protocol is compact JSON over
  UDP and requires no Qt. MeteoHub and GatewayLab are currently discovered by
  TCP probe, which assumes their mDNS name is known in advance — the opposite of
  discovery. A small emitter would let every morfSystem component be found the
  same way regardless of platform, and would retire the static lists in
  `morfsystem.json`.

- **State-change signals** — emit a Qt signal when `state()` changes, for
  reactive supervisors.
- **Optional authentication** on `/status` (shared token) for untrusted networks.
- **Headless configuration** — load `PresenceConfig` from a file / environment
  for services without a GUI.
- **IPv6 / multicast** option alongside IPv4 broadcast.
- **English translation** of the `docs/fr/` guides under `docs/en/`.
