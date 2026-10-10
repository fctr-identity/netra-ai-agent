# Netra AI v0.1.0-beta.2

Released October 10, 2026. Docker: `fctrid/netra-ai-agent-for-entra:0.1.0-beta.2`
(Linux AMD64). The `beta` and `latest` tags follow this release.

- Updated Fctr portal branding, browser icons, and Netra AI display names.
- Clearer README, ordered Quick Start, AI provider guidance, and Teams setup.
- Fctr Source-Available License 1.0 and private security-reporting instructions.
- Corrected Teams package website, privacy, and license links.
- The portal version now falls back to its package version when no build override is set.

The published image includes the optional Teams dependencies; Teams remains
disabled until configured. Live Teams delivery and large-tenant capacity remain
unvalidated for this beta. See the [installation guide](docs/INSTALLATION.md#upgrading)
for upgrade steps and the [license](LICENSE) for the terms of this release.

The previous `0.1.0-beta.1` image and Git tag remain unchanged.

## v0.1.0-beta.1

First beta for Microsoft Entra ID, built on the same agent harness as Tako AI Agent.

- 53 curated read-only Microsoft Graph operations for commercial Entra tenants.
- Optional SQLite snapshots for fast SQL queries alongside live Graph access.
- Conversational web UI, follow-ups, saved results, tables, and exports.
- CLI queries and sync, local admin login, and optional Teams personal chat.
- Configurable AI providers and separate reasoning and coding models.
- Progress reporting, cancellation, and rate-limit notifications.

This beta supports one tenant per deployment. Results depend on permissions,
licensing, data freshness, and model quality. Large-tenant capacity has not yet
been benchmarked. See the [documentation](docs/README.md) for setup and limitations.
