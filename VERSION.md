# Netra AI v0.1.0-beta.3

Released October 10, 2026. Docker: `fctrid/netra-ai-agent-for-entra:0.1.0-beta.3`
(Linux AMD64). The `beta` and `latest` tags follow this release.

- Automatically retain API discovery evidence and exact retrieval code.
- Distinguish successful capped discovery samples from incomplete retrieval.
- Default group-member questions to direct membership unless nested membership is requested.
- Clearer discovery progress messages and first-login setup-token instructions.
- Updated frontend dependencies to resolve reported high-severity advisories.
- Added the supported Entra entity table to the README.

Validated the live ND-All-Users query against all 300 demo users, including sorting
and enabled status. This does not establish large-tenant capacity. The image includes
optional Teams dependencies; live Teams delivery remains unvalidated.

## v0.1.0-beta.2

Released October 10, 2026. Docker: `fctrid/netra-ai-agent-for-entra:0.1.0-beta.2`
(Linux AMD64). Superseded by `0.1.0-beta.3`; the versioned image remains available.

- Updated [Fctr](https://fctr.io) portal branding, browser icons, and Netra AI display names.
- Removed the unused Special Tools button, dialog, and startup request from the chat UI.
- Clearer README, ordered Quick Start, AI provider guidance, and Teams setup.
- [Fctr](https://fctr.io) Source-Available License 1.0 and private security-reporting instructions.
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
