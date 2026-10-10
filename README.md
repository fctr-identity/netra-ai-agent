<div align="center">
  <a href="https://fctr.io">
    <picture>
      <source media="(prefers-color-scheme: dark)" srcset="./media/brand/fctr-lockup-reverse.png">
      <source media="(prefers-color-scheme: light)" srcset="./media/brand/fctr-lockup-primary.png">
      <img src="./media/brand/fctr-lockup-primary.png" alt="Fctr" width="96">
    </picture>
  </a>

  <br>

  <h1>Netra - AI Agent for Microsoft Entra ID</h1>

  <p>
    <a href="#quick-start-docker">Quick start</a> ·
    <a href="#try-these-questions">Example questions</a> ·
    <a href="#why-netra">Why Netra</a> ·
    <a href="#ai-providers">AI providers</a> ·
    <a href="#documentation">Docs</a> ·
    <a href="#support-and-contributing">Support</a>
  </p>

  <p>
    <a href="VERSION.md">
      <img src="./media/badges/preview.svg" alt="v0.1.0-beta.1" width="120" height="22">
    </a>
    <a href="docker-compose.yml">
      <img src="./media/badges/docker.svg" alt="Docker: build from source" width="170" height="22">
    </a>
    <a href="docs/INSTALLATION.md">
      <img src="./media/badges/python.svg" alt="Python 3.12" width="88" height="22">
    </a>
  </p>

  <p>Built by the Fctr Identity team · Not affiliated with Microsoft</p>
</div>

---

Named after the Sanskrit word for “eye,” **Netra** helps you see and understand
your Microsoft Entra ID environment. It is an open-source AI agent (currently
supporting read-only endpoints) that turns questions about your directory into
answers you can explore, follow up on, and export.

Netra is built on the same agent harness as
[**Tako AI Agent for Okta**](https://github.com/fctr-id/okta-ai-agent), adapted for
Microsoft Entra ID with Microsoft Graph and optional SQLite snapshots.

Ask questions in plain English and keep investigating in the same conversation.
Run Netra locally with your preferred supported LLM provider, through the browser,
CLI, or optional Microsoft Teams integration.

## Why Netra?

### How does Netra compare with other Entra AI tools and MCP servers?

**Netra brings the complete investigation workflow into one self-hosted product**—from
finding and processing directory data to follow-up conversations and exports.
Its strength is how these capabilities work together. Here's what sets Netra apart:

- 📊 **More data, less model context.** Code processes the records; the model receives compact previews and focused results instead of entire intermediate datasets.
- ⚡ **Fast SQL plus live Graph access.** Optional SQLite snapshots speed up repeat questions, while live APIs provide fresh or additional data.
- 💬 **Keep the conversation going.** Follow up with “Now show their applications” or “Which of those users are disabled?”
- 🔎 **Investigate across your directory.** Netra coordinates SQL, API queries, and analysis to answer questions that span multiple resources.
- 🔁 **Reuse successful workflows.** When enabled, compatible saved procedures can run again, with fresh orchestration if reuse fails.
- 🏠 **Run locally. Choose your model.** Self-host the complete application and use your preferred supported LLM provider.

Netra is in beta for one commercial Entra tenant per deployment. Results depend on
permissions, licensing, data freshness, and model quality. Large-tenant capacity
and comparative performance have not yet been benchmarked.

### Where your data comes from

- **Live Graph API:** ask questions without syncing first.
- **Local SQLite:** sync selected directory data for fast SQL queries.
- **Both:** combine synced and live data when an investigation needs them.

Ask “Using live Graph…” when you want current data. See
[what Netra syncs](docs/DATA_SYNC.md#what-netra-syncs) for the complete table.

## Quick start (Docker)

You need Docker Compose, a commercial Entra tenant, and a supported model provider.
The initial setup assumes Entra P1. For a local installation with **uv**, follow
[Installation and Entra setup](docs/INSTALLATION.md).

Docker Hub repository: [fctrid/netra-ai-agent-for-entra](https://hub.docker.com/r/fctrid/netra-ai-agent-for-entra).
No image tags are published yet; the steps below build from source.

1. Clone this repository and enter its directory:

   ```bash
   git clone https://github.com/fctr-identity/netra-ai-agent.git
   cd netra-ai-agent
   ```

2. [Register a single-tenant Entra application](docs/INSTALLATION.md#entra-app-registration)
   and grant the required read-only Graph application permissions. No redirect URI
   is needed. The default sync uses `User.Read.All`, `Group.Read.All`,
   `Application.Read.All`, and `AuditLog.Read.All`.

3. Copy [`.env.example`](.env.example) to `.env` if you don't already have one.
   Configure your Entra credentials and one model provider:

   ```dotenv
   ENTRA_TENANT_ID=<tenant-id>
   ENTRA_CLIENT_ID=<application-client-id>
   ENTRA_CLIENT_SECRET=<client-secret-value>

   AI_PROVIDER=openai_compatible
   OPENAI_COMPATIBLE_BASE_URL=<provider-api-base-url>
   OPENAI_COMPATIBLE_TOKEN=<provider-api-key>
   OPENAI_COMPATIBLE_REASONING_MODEL=<model-id>
   OPENAI_COMPATIBLE_CODING_MODEL=<model-id>
   ```

4. Build and start Netra:

   ```bash
   docker compose up --build -d
   docker compose logs -f netra
   ```

5. Open **http://127.0.0.1:8001**. Use the one-time setup token printed in the
   logs to create your local admin account.

6. Ask a question using live data, or select **Data sync → Sync now** to populate
   the local database first. Continue with follow-ups and export the results.

## Try these questions

- “Using live Graph, list users in Engineering with their job titles and enabled status.”
- “Which users belong to both the Engineering and Project Atlas groups?”
- “Which enterprise apps are assigned to this user directly or through their direct groups?”
- “Which users have an MFA registration record, and which are registered or capable?”
- “What does this Conditional Access policy include and exclude?”
- “From those results, show only disabled users.”

Replace names with ones from your tenant. Some questions need additional read
permissions. Browse the [question library](docs/QUESTION_LIBRARY.md) for more
examples. AI can make mistakes; validate results before acting on them.

## AI providers

Netra supports OpenAI, Google AI Studio, Google Vertex AI, Anthropic, Azure OpenAI,
AWS Bedrock, and OpenAI-compatible endpoints, including local models through Ollama.

Set `AI_PROVIDER` and configure your provider's credentials and model IDs. Reasoning
and coding can use the same model or different models. Choose models that support
structured tool calls; answer quality, speed, and cost vary by model.

### Models tested with Tako

[Tako's AI provider guide](https://github.com/fctr-id/okta-ai-agent#ai-provider-support)
lists these tested models for the shared agent harness:

| Provider | Model |
| --- | --- |
| DeepSeek | DeepSeek V4.1 Flash |
| Z.ai | GLM 5.3 |
| Google | Gemini 3.8 Flash |
| OpenAI | GPT-5.6 Terra |
| Anthropic | Claude Haiku 4.5 |

DeepSeek and Z.ai connect through `openai_compatible`. This list reflects Tako's
testing; try your chosen model with representative Entra questions before relying
on its results. Smaller, older, or untested models may give less reliable answers.

See [installation](docs/INSTALLATION.md) and [`.env.example`](.env.example) for
configuration. Prompts and selected directory context go to your configured model
provider, even when Netra itself runs locally.

## CLI and Teams

Run a query or refresh the database from the terminal:

```bash
uv run scripts/netra-cli.py "List enabled users in Engineering"
uv run scripts/sync_entra_to_db.py
```

See the [CLI and scheduling guide](docs/DATA_SYNC.md). Optional
[Teams personal chat](src/integrations/teams/README.md) uses the same query runtime.

## Documentation

| Guide | What it covers |
| --- | --- |
| [Installation and Entra setup](docs/INSTALLATION.md) | uv, Docker, Graph permissions, model configuration, and first login. |
| [Data sync and CLI](docs/DATA_SYNC.md) | Synced fields, optional datasets, custom attributes, scheduling, and exports. |
| [Question library](docs/QUESTION_LIBRARY.md) | Simple and advanced administrator questions. |
| [Supported Graph endpoints](docs/SUPPORTED_GRAPH_READS.md) | All 53 supported GET operations, permissions, and coverage. |
| [Runtime and data](docs/RUNTIME_AND_DATA.md) | Execution controls, local storage, retention, progress, and limitations. |
| [Development](docs/DEVELOPMENT.md) | Checks and catalog maintenance. |

The [documentation hub](docs/README.md) also links to the Teams and coverage guides.
The [GitHub Wiki](https://github.com/fctr-identity/netra-ai-agent/wiki) is enabled;
its landing page is being prepared.

## Support and contributing

Report bugs or suggest improvements through [GitHub Issues](https://github.com/fctr-identity/netra-ai-agent/issues).
Include reproduction steps and redacted errors; keep credentials and tenant data
out of reports. See the [development guide](docs/DEVELOPMENT.md) to contribute.

## License and attribution

Netra shares its agent harness with Fctr's [Tako AI Agent](https://github.com/fctr-id/okta-ai-agent).
See [LICENSE](LICENSE) for the current terms
and [third-party notices](THIRD_PARTY_NOTICES.md) for Microsoft metadata attribution.
