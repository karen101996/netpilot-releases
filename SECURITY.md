# Security Policy

## Security model

NetPilot stores device credentials locally in `%USERPROFILE%\TelnetManager\credentials.json`. Passwords are protected using Windows DPAPI in the context of the current Windows user.

**Important:** Telnet is a plaintext network protocol. Local DPAPI encryption does not protect credentials or session data in transit. Only use Telnet on trusted, isolated management networks. Prefer SSH when the device supports it.

The public updater uses HTTPS and verifies downloaded files against Git blob SHA-1 values in the published version manifest. This is an integrity check **against that manifest**, not a digital signature or an independent trust anchor. Signed releases are planned.

## Reporting vulnerabilities

Please avoid posting device IPs, credentials, configuration backups, tokens, or sensitive network topology in public issues.

For non-sensitive bugs, use the repository's [Issues](https://github.com/karen101996/netpilot-releases/issues). For a sensitive vulnerability, contact the maintainer privately using an available private GitHub contact method before disclosing technical details publicly.

## Supported versions

Only the latest published stable version is intended for ongoing support. Older versions may receive no security fixes.
