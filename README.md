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
    <a href="#from-a-question-to-an-investigation">Demo</a> ·
    <a href="#what-can-netra-ai-answer-today">Coverage</a> ·
    <a href="#try-these-questions">Example questions</a> ·
    <a href="#why-netra-ai">Why Netra AI</a> ·
    <a href="#ai-provider-support">AI providers</a> ·
    <a href="#microsoft-teams">Teams</a> ·
    <a href="#documentation">Docs</a> ·
    <a href="#community-and-support">Support</a>
  </p>
  <p>
    <a href="VERSION.md">
      <img src="./media/badges/preview.svg" alt="v0.1.0-beta.3" width="120" height="22">
    </a>
    <a href="docker-compose.yml">
      <img src="./media/badges/docker.svg" alt="Docker: Linux AMD64" width="170" height="22">
    </a>
    <a href="docs/INSTALLATION.md">
      <img src="./media/badges/python.svg" alt="Python 3.12" width="88" height="22">
    </a>
  </p>
  <p>Built by the Fctr Identity team · Not affiliated with Microsoft</p>
</div>

---

Named after the Sanskrit word for “eye,” **Netra AI** helps you see and understand
Microsoft Entra ID. Ask about users, groups, applications, devices, and access in
plain English, then explore the answers, ask follow-ups, and export the results.

Netra AI is a **source-available AI agent (currently supporting [read-only endpoints](docs/SUPPORTED_GRAPH_READS.md))**,
with a web UI, CLI, and optional Microsoft Teams integration.

**Built on the same agent harness as [Tako AI Agent for Okta](https://github.com/fctr-id/okta-ai-agent).**
Netra AI brings Tako's multi-agent orchestration, conversational UI, and combined
database and live-API approach to Microsoft Entra ID. The shared foundation powers
the workflow; Netra AI adapts the directory schema, API catalog, and prompts for
Microsoft Graph and Entra administration.

## From a question to an investigation

Watch Netra AI retrieve 300 demo users, then use the saved results to find the
30 disabled accounts in a follow-up.

![Netra AI retrieves 300 users and filters the saved results in a follow-up](media/demo/netra-ai-demo-1.gif)

[Watch or download the full video](media/demo/netra-ai-demo-1.mp4).

## Why Netra AI?

**How does Netra AI compare with other Entra AI tools and MCP servers?**

**Your directory shouldn't have to fit inside an LLM's context window.** Asking
for 100, 10,000, or 50,000 users should not require passing every user's record
through the model. Netra AI uses code to retrieve and process directory data, saves
results outside the model's context, and makes retrieved rows available in tables
and CSV exports. The model works with compact previews and focused results;
those previews do not set the size of your saved dataset.

Compared with MCP tools that return raw records directly into model context,
this approach reduces context usage as datasets grow. Netra AI packages it with a
web UI, follow-ups, and exports in one application. Here's why that matters:

- 📊 **Fewer tokens. Lower AI costs.** Netra AI processes bulk data in code and sends compact previews to the model, reducing input-token costs compared with passing every retrieved record into context. Saved results remain available for tables and CSV exports.
- 💰 **Premium models aren't required.** Use lower-cost Flash models such as Gemini Flash to keep model costs down.
- ⚡ **Fast SQL plus live Graph access.** Optional SQLite snapshots speed up repeat questions, while live APIs provide fresh or additional data.
- 💬 **Keep the conversation going.** Follow-ups build on previous results, so you can narrow a population or investigate its applications.
- 🔎 **Investigate across your directory.** Netra AI coordinates SQL, API queries, and analysis for questions that span multiple resources.
- 🔁 **Reuse successful workflows.** When enabled, compatible saved procedures run again, with fresh orchestration if reuse fails.
- 🏠 **Run locally. Choose your model.** Self-host the application and use your preferred supported AI provider.

**Beta:** one commercial Entra tenant per deployment. Results depend on permissions,
licensing, data freshness, model quality, and execution limits. The sizes above
illustrate the approach, not validated capacity: 10,000- and 50,000-user Netra AI runs
and comparative performance have not yet been benchmarked.

## What can Netra AI answer today?

Netra AI currently supports 53 read-only Microsoft Graph operations covering the
Entra entities and relationships below. Coverage can expand as more Graph
endpoints are added.

| Entity or area | What you can explore |
| --- | --- |
| Users | Members and guests, profile attributes, enabled status, direct reports, and group memberships. |
| Groups | Group details, owners, direct and nested membership, and parent groups. |
| Applications | Enterprise apps (service principals), app registrations, and their owners. |
| App assignments and consent | User and group app-role assignments, application permissions granted to service principals, and delegated consent grants. |
| Devices | Entra device details, enabled status, operating systems, registered owners, and registered users. |
| MFA registrations and authentication methods | MFA registration and capability reports, plus registered methods for an individual user. |
| Conditional Access | Policy state, conditions, controls, named locations, and authentication strengths. |
| Authentication-method policy | Tenant method configuration, target groups, and registration enforcement. |
| Directory roles | Role definitions, current assignments, assigned principals, and scopes. |
| Sign-in and audit logs | Retained sign-in events and directory changes within a requested time window. |
| Administrative units | Unit details and direct members. |
| Tenant, domains, and licenses | Organization details, domain settings, subscribed license SKUs, service plans, and consumed license counts. |

Coverage depends on your app permissions, Entra licensing, and available data.
See the [full endpoint list](docs/SUPPORTED_GRAPH_READS.md) for supported operations
and requirements, or [what syncs to SQLite](docs/DATA_SYNC.md#what-netra-ai-syncs) for database coverage.

## Try these questions

| Start with… | Ask Netra AI |
| --- | --- |
| Users · Simple | “Using live Graph, list users in Engineering with their job titles and enabled status.” |
| Devices · Simple | “List disabled Entra devices with their operating systems.” |
| Groups · Advanced | “Which users belong to both the Engineering and Project Atlas groups?” |
| App assignments · Advanced | “Which enterprise apps are assigned to this user directly or through their direct groups?” |
| MFA registrations | “Which users have an MFA registration record, and which are registered or capable?” |
| Conditional Access | “What does this Conditional Access policy include and exclude?” |

Replace names with ones from your tenant; some questions need additional permissions.
Browse the [question library](docs/QUESTION_LIBRARY.md) and [Graph endpoints](docs/SUPPORTED_GRAPH_READS.md).
Validate AI-generated results before acting on them.

## Quick start (Docker)

You need Docker Compose, a commercial Entra tenant, and a supported AI provider.
The published [Docker image](https://hub.docker.com/r/fctrid/netra-ai-agent-for-entra)
uses `latest` for **Linux AMD64**. Prefer a local install? Follow the [uv guide](docs/INSTALLATION.md).

1. **[Create the Entra application](docs/INSTALLATION.md#entra-app-registration).**
   Register a single-tenant app and create a client secret. Entra creates its
   matching Enterprise Application automatically; no redirect URI is needed.
2. **[Assign Graph permissions](docs/INSTALLATION.md#graph-permissions-and-admin-consent).**
   Add the required read-only application permissions and grant admin consent.
3. **Download the Docker configuration.** Only two files are needed:

   ```bash
   mkdir netra-ai-agent
   cd netra-ai-agent
   curl -fL -o docker-compose.yml https://raw.githubusercontent.com/fctr-identity/netra-ai-agent/v0.1.0-beta.3/docker-compose.yml
   curl -fL -o .env.example https://raw.githubusercontent.com/fctr-identity/netra-ai-agent/v0.1.0-beta.3/.env.example
   ```

   In Windows PowerShell, use `curl.exe` instead of `curl`.

4. **Configure credentials and AI.** Copy [`.env.example`](.env.example) to `.env`
   if one does not already exist. Add your [Entra credentials](docs/INSTALLATION.md#entra-credentials)
   and [AI provider settings](docs/INSTALLATION.md#ai-provider-configuration).
   See [AI Provider Support](#ai-provider-support) for the provider and model list.
5. **[Start Netra AI with Docker](docs/INSTALLATION.md#docker).**

   ```bash
   docker compose pull
   docker compose up -d
   docker compose logs -f netra
   ```

6. **[Complete first login](docs/INSTALLATION.md#first-login).** On first startup,
   look for this message in the Docker logs above:

   ```text
   [netra-ai-agent] INITIAL SETUP REQUIRED
   [netra-ai-agent] Setup token: <your-generated-token>
   ```

   Open **http://127.0.0.1:8001**, enter that token, and create your local admin
   account. The token is generated for your instance, is used once, and changes
   if you restart before completing setup. After setup, sign in with your username
   and password. Try an [example question](#try-these-questions), or select
   **Data sync → Sync now** to prepare the [optional database](docs/DATA_SYNC.md#what-netra-ai-syncs)
   for faster queries.

## AI Provider Support

Netra AI supports OpenAI, Google AI Studio, Google Vertex AI, Anthropic, Azure OpenAI,
AWS Bedrock, and OpenAI-compatible endpoints, including local models through Ollama.

**You don't need a premium model.** Netra AI supports Flash models such as Gemini
Flash alongside larger models. Choose a model that gives reliable answers to
your Entra questions at a cost you're comfortable with.

Set `AI_PROVIDER` and fill in that provider's section in `.env`. You can use the
same model for reasoning and coding, or a different model for each. Model choice
affects answer quality, speed, and cost. See the [configuration guide](docs/INSTALLATION.md#ai-provider-configuration).

### Models

| Provider | Model |
| --- | --- |
| DeepSeek | DeepSeek V4.1 Flash |
| Z.ai | GLM 5.3 |
| Google | Gemini 3.8 Flash |
| OpenAI | GPT-5.6 Terra |
| Anthropic | Claude Haiku 5.5 |

DeepSeek and Z.ai connect through `openai_compatible`. Try your chosen model with
representative Entra questions first. Smaller, older, or untested models may give
less reliable answers. See the [provider and model guide](docs/AI_PROVIDERS.md) for context.

### Reasoning setting

Optionally set `AI_REASONING_EFFORT=high` to request more reasoning; this can make
answers slower and more expensive. If your model does not support the setting,
use `AI_REASONING_EFFORT=none` or leave it unset, then restart Netra AI. Both leave
the model's defaults intact; some models still reason by default.

## Microsoft Teams

Ask questions, continue follow-ups, and download CSV results in a personal Teams
chat, with access restricted to your tenant and allowed groups. Teams is optional
and disabled by default; the Docker image includes its dependencies. Follow the
[Teams setup guide](src/integrations/teams/README.md). Live Teams delivery has not
yet been validated for this beta.

## Upgrading

Back up your data and check the [release notes](VERSION.md) and
[upgrade guide](docs/INSTALLATION.md#upgrading), then run:

```bash
docker compose pull
docker compose up -d
```

## Documentation

| Guide | What you'll find |
| --- | --- |
| [Installation](docs/INSTALLATION.md) | Docker, manual setup with uv, Entra permissions, and first login. |
| [Data sync and CLI](docs/DATA_SYNC.md) | Exactly what is synced, custom attributes, scheduling, and terminal queries. |
| [Graph coverage](docs/SUPPORTED_GRAPH_READS.md) | Supported GET endpoints, permissions, and coverage limits. |
| [Development](docs/DEVELOPMENT.md) | Local checks and extending Netra AI. |

Browse the [documentation hub](docs/README.md) for all guides.

## Security and privacy

Netra AI uses read-only Graph access. Prompts and selected directory data go to your
configured AI provider, even when Netra AI runs locally. Protect local snapshots,
conversation history, saved results, and logs as sensitive tenant data.

We work to improve security, but cannot guarantee freedom from vulnerabilities.
Netra AI is provided **“as is,” without warranty**.
Report suspected vulnerabilities privately through the [security policy](.github/SECURITY.md).

## Community and support

- 🐛 [GitHub Issues](https://github.com/fctr-identity/netra-ai-agent/issues) — Bugs and feature requests; redact credentials and tenant data.
- 📧 [support@fctr.io](mailto:support@fctr.io) — General support.
- 🤝 Contributions welcome — improve docs, suggest questions, or extend Graph coverage. Discuss larger changes in an issue and follow the [development guide](docs/DEVELOPMENT.md).
- [Contributors](https://github.com/fctr-identity/netra-ai-agent/graphs/contributors).

## License

[Fctr Source-Available License 1.0](LICENSE): personal and internal organizational
use is free. Resale, paid derived products, and hosted, SaaS, MSP, or multi-tenant
service offerings require a separate commercial license. See the full terms and
[third-party notices](THIRD_PARTY_NOTICES.md).
