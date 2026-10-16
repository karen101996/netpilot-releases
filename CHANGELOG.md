## v1.5.8 — TP-Link enable prompt synchronization

- Send an empty line after TP-Link's login notification and wait for a fresh CLI prompt before automatic `enable`.
- Keep other devices' enable flow unchanged.

## v1.5.7 — TP-Link automatic enable timing

- Add a short settling delay before automatic `enable` after TP-Link's login event.
- Leave the enable timing for other supported network equipment unchanged.

## v1.5.6 — TP-Link interactive login

- Detect the TP-Link `Login the CLI by ... on vty...` success event after authentication.
- Enter interactive mode when the device confirms a successful login, even if its prompt is interleaved with a timestamped event.
- Preserve existing prompt matching and authentication failure checks.

## v1.5.5 — TP-Link CLI prompt detection

- Recognize TP-Link prompts followed immediately by timestamped login events.
- Preserve standard network CLI prompt handling.

## v1.5.4 — TP-Link Telnet login compatibility

- Recognize `User:` prompts in addition to `Login:` and `Username:`.
- Automatically continue saved-credential authentication on compatible TP-Link devices.

## v1.5.3 — Telnet navigation keys

- Forward Up/Down and Left/Right arrow keys to the remote Telnet CLI.
- Forward Home, End, and Delete keys using terminal escape sequences.
- Remote device support for command history and editing may vary.

## v1.5.2 — Installer syntax fix

- Repair the malformed PowerShell installer in v1.5.1.
- Keep legacy v1.2.x updater compatibility and checksum-verified SSH module retrieval.
- Add PowerShell parser validation to CI before release publication.

## v1.5.1 — Legacy upgrade fix

- Fix upgrades from older RAVLAN/NetPilot v1.2.x installations: the old updater does not download `ssh_password.py`.
- Installer now securely retrieves the missing module and validates its Git blob SHA against the release manifest.
- Existing aliases and saved credentials remain unchanged.

## v1.5.0 — RAVLAN rebrand

- Renamed the product to **RAVLAN** and introduced the `rv` management command.
- Kept the legacy `np` command, installation location, and encrypted credentials compatible.
- Updated release repository links and documentation.

# Changelog

## [1.4.4] — 2026-10-12
- Use `s NAME --reset` to replace a saved SSH password.
- Keep passwords for other devices unchanged.
- Save the replacement password only after successful SSH authentication.

## [1.4.3] — 2026-10-12
- Save SSH passwords encrypted with Windows DPAPI after successful login.
- Reuse saved SSH passwords automatically, including Win+R aliases.
- Verify SSH host keys before trusting new devices.
- Include the interactive SSH module in updates and installers.

## [1.4.0] — 2026-10-12
- SSH connections using `s IP` and `s ALIAS`.
- Win+R shortcuts for saved devices, with Telnet/SSH protocol selection.
- Colorful `rv help` in Russian, English, and Uzbek.
- Persistent `rv language ru|en|uz` and `rv version`.
- Signed Python installer fallback when winget is unavailable.
- Existing credentials remain unchanged.

## [1.3.0] — 2026-10-12
- Added a local device address book with `t add NAME IP`, `t list` and `t search QUERY`.
- Connect to saved devices by alias using `t NAME`.
- Kept existing `t IP` connections and Windows DPAPI credential storage compatible.
- Added release notes display after successful `rv update` (starting with updates performed by the v1.3.0 updater).
- Fixed newline rendering in update notifications.
- Added Windows CI regression tests for address book operations.

All notable RAVLAN changes are documented here. Versions below summarize the observed development milestones; release notes are not a substitute for automated test results.

## [1.2.5] — 2026-10-12
- Added cache-busting to the public version check performed before Telnet connections.
- Improved the notification flow for available updates.
- Kept update checks non-blocking for device connections.

## [1.2.4] — 2026-10-12
- Fixed stale GitHub API responses in the PowerShell updater.
- Verified the update flow from v1.2.3 to v1.2.4 on Windows.

## [1.2.3] — 2026-10-12
- Verified downloading, checksum checking and installing updates with `rv update`.

## [1.2.2] — 2026-10-12
- Switched update checks and downloads from raw GitHub URLs to the public GitHub Contents API.

## [1.2.1] — 2026-10-12
- Test release for the public update channel.

## [1.2.0] — 2026-10-12
- Added unauthenticated public update distribution.
- Added `rv update` and version notifications on connection.
- Preserved locally stored credentials across upgrades.

## Next
See [ROADMAP.md](ROADMAP.md) for planned features. Features listed there are not yet implemented.
