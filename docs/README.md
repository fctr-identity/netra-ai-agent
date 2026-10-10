# Netra documentation

Netra answers administrator questions using a curated set of read-only Microsoft
Graph operations and selected local snapshots. It runs locally for one commercial
Entra tenant per deployment. The question library includes scenarios relevant to
small, medium, and large tenants; it does not establish enterprise-scale capacity.

| I want to… | Start here |
| --- | --- |
| Install and start Netra | [Installation and Entra setup](INSTALLATION.md) |
| Configure credentials and permissions | [Entra app registration](INSTALLATION.md#entra-app-registration) |
| Choose and configure a model | [AI providers and models](AI_PROVIDERS.md) |
| Upgrade an existing installation | [Upgrade guide](INSTALLATION.md#upgrading) |
| See exactly what is synced | [Synced datasets and fields](DATA_SYNC.md#what-netra-syncs) |
| Refresh snapshots, schedule sync, or use the CLI | [Data sync and CLI](DATA_SYNC.md) |
| Understand execution, storage, and cleanup | [Runtime and data](RUNTIME_AND_DATA.md) |
| Run checks or contribute | [Development](DEVELOPMENT.md) |
| Set up Teams personal chat | [Teams integration](../src/integrations/teams/README.md) |
| Find questions to ask | [Administrator question library](QUESTION_LIBRARY.md) |
| See every supported GET endpoint | [Supported Graph reads](SUPPORTED_GRAPH_READS.md) |
| Understand exclusions or add an endpoint | [Catalog guide](GRAPH_CATALOG.md) |
| Check the metadata sources | [Catalog provenance](graph_catalog_sources.json) |

## Choose the scope before running a report

- **Explore:** request a small sample to understand the available fields.
- **Investigate:** name a user, group, app, device, department, or administrative
  unit. Prefer an object ID when display names are ambiguous.
- **Report:** specify a population and ask for an aggregate or exceptions first.
  Request complete pagination and an explicit indication of partial coverage.
  Broader requests may exceed the POC's execution or model limits.

For supported snapshot data, a recent local sync can reduce repeated live reads.
Ask for live data when current state matters or the resource is live-only.
Sign-ins and audits require a time window. A successful sample does not establish
a tenant-wide total, and a failed read does not establish that no objects exist.

## What “supported” means

The endpoint inventory is generated from the same reviewed catalog used by the
adapter. It documents implemented paths and selected permissions; it is not a
claim that every path or question has been verified in every tenant. Feature
licensing, consent, report freshness, and visibility determine the evidence
available. The catalog guide records explicit exclusions and alternatives.

The query UI reports Graph/model throttling and provider retry hints. Existing
deadlines still apply. A retry hint is not a guaranteed quota-reset time.

## Documentation and GitHub Wiki

Keep these documents in the code repository so endpoint and documentation changes
can be reviewed together. The runtime catalog remains the authority for endpoint
coverage; do not hand-maintain a second endpoint list in a Wiki.

[Wiki Home source](wiki/Home.md) provides a short landing page with links to these
documents. Its links target `main`, so publish the linked documentation to `main`
before publishing that page. Create the Wiki's initial Home page and use this source
as its content. Subsequent changes can use the Wiki's separate Git repository.
Keep Wiki editing restricted to collaborators.

The [repository Wiki](https://github.com/fctr-identity/netra-ai-agent/wiki) is enabled
(checked October 10, 2026), but its Git repository is not accessible yet. Initialize
it by saving the first page through GitHub. README links point to the checked-in
guides until the prepared landing page is published.

The Wiki page is navigation only. Update the documents here for new questions,
setup changes, and endpoint coverage. Human documentation links are not added to
the runtime agent catalog or model context.
