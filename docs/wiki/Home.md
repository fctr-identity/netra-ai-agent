# Netra AI

Netra AI is a source-available AI agent in beta for asking administrator questions about Microsoft
Entra ID. It combines read-only Microsoft Graph queries with selected local
snapshots, a conversational UI, and optional Teams personal chat.

Start with one commercial Entra tenant and a local deployment. Examples cover
small and large tenant scenarios; enterprise-scale performance is not yet established.

## Start here

- [Docker image](https://hub.docker.com/r/fctrid/netra-ai-agent-for-entra) (`0.1.0-beta.2`, Linux AMD64)
- [Install Netra AI with uv or Docker](https://github.com/fctr-identity/netra-ai-agent/blob/main/docs/INSTALLATION.md)
- [Register the Entra app and configure read permissions](https://github.com/fctr-identity/netra-ai-agent/blob/main/docs/INSTALLATION.md#entra-app-registration)
- [See synced datasets and fields](https://github.com/fctr-identity/netra-ai-agent/blob/main/docs/DATA_SYNC.md#what-netra-ai-syncs)
- [Sync data and run CLI queries](https://github.com/fctr-identity/netra-ai-agent/blob/main/docs/DATA_SYNC.md)
- [Run development checks](https://github.com/fctr-identity/netra-ai-agent/blob/main/docs/DEVELOPMENT.md)
- [Browse Simple and Advanced administrator questions](https://github.com/fctr-identity/netra-ai-agent/blob/main/docs/QUESTION_LIBRARY.md)
- [See every supported Graph GET endpoint](https://github.com/fctr-identity/netra-ai-agent/blob/main/docs/SUPPORTED_GRAPH_READS.md)
- [Understand coverage boundaries and contribute endpoints](https://github.com/fctr-identity/netra-ai-agent/blob/main/docs/GRAPH_CATALOG.md)
- [Documentation guide](https://github.com/fctr-identity/netra-ai-agent/blob/main/docs/README.md)

The endpoint reference includes application permissions, feature availability,
and live/sync coverage. It is generated from the runtime catalog and is the
authoritative endpoint list. The question library contains suggested workflows,
not a claim that every question has been live-tested in every tenant.

Detailed documentation lives with the code so changes can be reviewed together.
This Wiki provides navigation to those documents; it does not maintain a separate
copy of setup instructions or endpoint coverage.
