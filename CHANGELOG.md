# Changelog

## [1.3.0] — 2026-10-12
- Added a local device address book with `t add NAME IP`, `t list` and `t search QUERY`.
- Connect to saved devices by alias using `t NAME`.
- Kept existing `t IP` connections and Windows DPAPI credential storage compatible.
- Added release notes display after successful `np update` (starting with updates performed by the v1.3.0 updater).
- Fixed newline rendering in update notifications.
- Added Windows CI regression tests for address book operations.

All notable NetPilot changes are documented here. Versions below summarize the observed development milestones; release notes are not a substitute for automated test results.

## [1.2.5] — 2026-10-12
- Added cache-busting to the public version check performed before Telnet connections.
- Improved the notification flow for available updates.
- Kept update checks non-blocking for device connections.

## [1.2.4] — 2026-10-12
- Fixed stale GitHub API responses in the PowerShell updater.
- Verified the update flow from v1.2.3 to v1.2.4 on Windows.

## [1.2.3] — 2026-10-12
- Verified downloading, checksum checking and installing updates with `np update`.

## [1.2.2] — 2026-10-12
- Switched update checks and downloads from raw GitHub URLs to the public GitHub Contents API.

## [1.2.1] — 2026-10-12
- Test release for the public update channel.

## [1.2.0] — 2026-10-12
- Added unauthenticated public update distribution.
- Added `np update` and version notifications on connection.
- Preserved locally stored credentials across upgrades.

## Next
See [ROADMAP.md](ROADMAP.md) for planned features. Features listed there are not yet implemented.
