# Contributing to morfBeacon

Thanks for your interest! morfBeacon is a small, shared library: it must stay
**tiny, portable and dependency-light**, because it is compiled into every app of
the workshop (ComponentHub, SiteWatch, future tools).

## 1. Philosophy

- **Small surface.** Five pieces (`PresenceConfig`, `IMetricsProvider`,
  `Heartbeat`, `StatusServer`, `PresenceService`). Resist growing the API.
- **Qt Core + Network only.** No Widgets, no extra third-party dependency: the
  library must work in a headless service.
- **Portable by construction.** No platform- or architecture-specific code
  (no `#ifdef _WIN32`, no intrinsics, no endianness assumptions). It must behave
  identically on Windows, Linux x64 and Raspberry Pi (ARM64).

## 2. Building and testing

```sh
cmake --preset mingw      # or linux / linux-arm64
cmake --build --preset mingw
```

Then, in two terminals, exercise the real path:

```sh
./build-mingw/examples/minimal/morfbeacon_demo
python tools/fake_dashboard.py --poll --every 10
```

You should see discovery, `/status` metrics and offline transitions.

## 3. Coding conventions

- C++17, Qt idioms (parent/child ownership, signals/slots where relevant).
- Keep each source file with an SPDX header: `SPDX-License-Identifier: GPL-3.0-only`.
- Comments in French are fine (they match the existing code).

## 4. Changing the protocol

The wire format is specified in [docs/fr/PROTOCOL.md](docs/fr/PROTOCOL.md). Any
**incompatible** change to the heartbeat or `/status` format must bump the
protocol version (`morfbeacon/2`) and be documented there — supervisors ignore
protocols they don't understand.

## 5. Documentation language

Root documents (`README.md`, `CHANGELOG.md`, `ROADMAP.md`, this file) are in
**English**; a French `README.fr.md` is kept. The in-depth guides live under
`docs/fr/` (French, the reference language). Update the matching document when
you change behavior.

## 6. Reporting bugs / proposing changes

Use **GitHub Issues** to report a problem or suggest an improvement, and open a
pull request for changes.
