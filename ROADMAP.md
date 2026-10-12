# NetPilot Roadmap

NetPilot is a Windows CLI for SSH and Telnet device access. This roadmap separates **shipped features** from ideas under consideration.

## Shipped — v1.4.4

- [x] SSH and Telnet interactive connections
- [x] Save device aliases and connect by name
- [x] Windows Run (`Win + R`) shortcuts
- [x] Encrypt SSH and Telnet passwords locally with Windows DPAPI
- [x] Reuse saved credentials automatically
- [x] Reset saved SSH and Telnet credentials
- [x] SSH host-key verification
- [x] Configure SSH usernames per device
- [x] Russian, English and Uzbek command help
- [x] Versioned public releases and verified update manifests
- [x] Automated Python checks and regression tests

## Planned / under consideration

- [ ] Installation diagnostics (`np doctor`)
- [ ] Network reachability diagnostics
- [ ] Optional local connection history
- [ ] Read-only device configuration backups
- [ ] Installer and updater integration tests on clean Windows systems
- [ ] Digitally signed release artifacts and signature verification
- [ ] Documented uninstall and rollback workflows
- [ ] More device-specific terminal compatibility testing

## Compatibility commitments

- Keep `t IP`, `s IP` and saved device aliases working.
- Preserve existing DPAPI-protected credentials during normal updates.
- Never upload device credentials to the release repository.
- Do not silently change network device configurations.

See the [README](README.md) for commands and [CHANGELOG](CHANGELOG.md) for released changes.
