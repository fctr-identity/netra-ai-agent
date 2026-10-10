# Netra v0.1.0-beta.1

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
