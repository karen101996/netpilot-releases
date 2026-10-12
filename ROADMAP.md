# NetPilot Roadmap

NetPilot development is organized into small, verifiable stages. **Planned does not mean implemented.**

## Stage 1 — Public project presentation
- [x] Professional bilingual README
- [x] Changelog, security policy and roadmap
- [ ] Original logo and header artwork
- [ ] Sanitized terminal screenshots / GIF demo
- [ ] Official GitHub Release with downloadable installer archive
- [ ] Installation and update smoke tests on a clean Windows system

## Stage 2 — Device address book
- [ ] `t list`: list saved devices (without exposing secrets)
- [ ] `t add <alias> <ip>`: save a friendly device name
- [ ] `t <alias>`: connect using a saved name
- [ ] `t search <query>`: search by alias or IP
- [ ] Migration tests preserving existing DPAPI credentials
- [ ] Explicit error handling for duplicate aliases and invalid IP addresses

## Stage 3 — Diagnostics and convenience
- [ ] `t ping <ip-or-alias>`
- [ ] Local connection history with privacy-conscious retention
- [ ] `np doctor`: diagnose installation, PATH, Python and update access

## Stage 4 — Configuration backups
- [ ] `t backup <ip-or-alias>`
- [ ] Vendor-specific, read-only configuration retrieval adapters
- [ ] Clear output directory and backup timestamps
- [ ] Tests to ensure no commands modify device configuration

## Stage 5 — SSH
- [ ] SSH connection support and protocol selection
- [ ] Host-key verification and trust-on-first-use workflow
- [ ] Secure authentication and compatibility testing

## Stage 6 — Release quality and security
- [ ] CI tests for parsing, device profiles, migrations and updates
- [ ] Installer / updater integration tests
- [ ] Signed releases and signature verification
- [ ] Versioned immutable release artifacts and reproducible packaging
- [ ] User-friendly uninstaller and rollback documentation

## Compatibility promises
- Keep `t IP` working.
- Keep `np update` working.
- Do not delete or publish local credentials.
- Do not silently change device configurations.
- Prefer opt-in new features and explicit migration steps.
