# Netra

Netra is a local, single-tenant AI assistant for Microsoft Entra ID.
This POC combines live Microsoft Graph reads with local
SQLite snapshots, an existing conversational UI, and optional Teams personal chat.

The first workflows cover users and group membership, enterprise app assignments,
and MFA registration. The read catalog also includes app registrations, directory
roles, Conditional Access policies, devices, and bounded sign-in/audit searches.
It targets the standard commercial cloud and assumes Entra P1. Feature permissions,
licensing, retention, and report freshness still determine the available evidence.

## Local setup

Use Python 3.12+ and Node.js 24. From the repository root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
npm --prefix src/frontend ci
npm --prefix src/frontend run build
```

On macOS/Linux, activate with `source .venv/bin/activate` and copy the template
with `cp .env.example .env`. Keep `.env` private.

Create a single-tenant Entra app registration. Add a client secret and configure
`ENTRA_TENANT_ID`, `ENTRA_CLIENT_ID`, and `ENTRA_CLIENT_SECRET`. Use the secret
**value**, not its identifier. Graph authentication uses Microsoft's async Azure
Identity library and Graph Python SDK with application permissions and admin consent.

| Read scope | Microsoft Graph application permissions |
| --- | --- |
| Users, groups, direct memberships; Teams group authorization | `User.Read.All`, `Group.Read.All` |
| Enterprise apps, app registrations, app-role assignments | `Application.Read.All` |
| MFA registration reports, sign-in and directory audit reads | `AuditLog.Read.All` |
| Optional directory role definitions and assignments | `RoleManagement.Read.Directory` |
| Optional Conditional Access policies | `Policy.Read.All` |
| Optional directory device inventory | `Device.Read.All` |

Grant only the scopes you enable. Hidden group membership additionally needs
`Member.Read.Hidden`. Permission failures are reported as unavailable evidence,
not as empty data. Netra does not need Graph write permissions.

Configure a model provider separately. The template defaults to
`AI_PROVIDER=openai_compatible`; set its base URL, token, reasoning model, and
coding model. Inherited provider adapters also support `openai`, `azure_openai`,
`google`, `vertex_ai`, `anthropic`, and `bedrock`. The template includes the
OpenAI and Azure alternatives. Choose models supporting structured tool calls.

Start the local server:

```powershell
python main.py
```

Open **http://127.0.0.1:8001**. The first start prints a one-time setup token in
the terminal; use it to create the local admin login. Entra credentials are for
directory reads and do not replace that login. The default server binds to
loopback. For a public HTTPS deployment, configure the proxy and set
`COOKIE_SECURE=true`. Use one API worker and one replica.

## Sync and query

Click **Data sync → Sync now**, or run the same snapshot engine once:

```powershell
python scripts/sync_entra_to_db.py
```

The CLI exits 0 for a complete sync and nonzero for partial/failing runs. There
is no built-in scheduler. Run this command with the virtual environment's Python
from cron or Windows Task Scheduler when needed. An OS lock coordinates CLI and
UI syncs. A stale process history does not prevent a fresh UI sync.

Default snapshots include users, groups, direct memberships, service principals,
app registrations, app-role assignments, and MFA registration. Set
`SYNC_DIRECTORY_ROLES`, `SYNC_CONDITIONAL_ACCESS`, or `SYNC_DEVICES` to `true` to
include optional resources. Set `SYNC_MFA_REGISTRATION=false` to omit that report.
Sign-in and audit events are queried live with an explicit time lower bound.

Each resource publishes only after all its reads complete. Failed refreshes retain
the prior snapshot and record the failure separately from its last success.
Empty successful snapshots are valid. Resources refresh independently, so a run
is not a transactionally consistent snapshot of the entire tenant.

Use `ENTRA_USER_CUSTOM_ATTRIBUTES` for comma-separated Graph user properties,
directory/schema extensions, and dotted `onPremisesExtensionAttributes` fields.
Selected values are stored in `users.custom_attributes`; missing values remain
null. Open extensions and custom security attributes are outside this initial
sync. Netra creates `sqlite_db/netra.db` with new
directory tables while retaining the shared login, history, result, and procedure
table designs. Databases from other directory providers are not migrated or reused.

Example questions:

- Which users belong directly to the Engineering group?
- Which enterprise apps are assigned to a named user, directly or through groups?
- Which users appear in the MFA registration report as not registered?

The CLI query interface is `python scripts/netra-cli.py --help`. Exported retrieval
scripts depend on this Netra checkout and its configured virtual environment.

## Teams

Teams is optional and uses the same query runtime. Install
`requirements-teams.txt`, configure the bot identity and allowed groups, and
follow [the Teams guide](src/integrations/teams/README.md). Bot Service needs a
reachable HTTPS messaging endpoint even when the Netra process runs locally.
The bot tenant must match `ENTRA_TENANT_ID`; authorization checks use Netra's
read-only Graph identity. Slack and specialized access analyses are outside this POC.

## Docker

After configuring `.env`, run `docker compose up --build`. This builds Netra locally
and exposes it on loopback port 8001, with named volumes for the database and chat
artifacts. Set `INSTALL_TEAMS_BOT=true` when building a Teams-enabled image. Use
`docker compose exec netra python scripts/sync_entra_to_db.py` for a one-shot sync.

## Runtime boundaries and data

The agent receives local descriptions, notes, parameters, and JSON response
contracts for **25 approved GET operations**, not the entire Microsoft Graph API.
The SDK adapter restricts directory traffic to those v1.0 paths on the commercial
Graph host and handles pagination/retries. OAuth token acquisition is separate
from the read-only directory calls. No agent browser or arbitrary HTTP tool is
provided. Model-bound context has external hyperlinks removed, including links
found in directory values and tool results; stored source data is retained.

Queries and selected directory data are sent to the configured model provider.
SQLite snapshots, conversation history, generated scripts, results, and logs are
local sensitive data; keep them out of Git. Generated-code validation and the
read-only SQL connection are POC guardrails, not an OS sandbox for hostile users.
Python validators enforce explicit imports/members and calls, reject opaque
string-format traversal and helper rebinding, and run before script staging or
saved-result analysis. Prompt instructions are not a security boundary. Accepted
Python still runs with the application's operating-system privileges.

Assignments are not effective access. MFA registration is not successful MFA use.
Direct and transitive memberships differ, and nested groups do not confer
group-based app assignments. The v1.0 group-members source has a documented
service-principal omission; Netra records that limit. PIM eligibility, risk
analysis, Intune management, and write operations are outside this release.

## Catalog maintenance and checks

See [catalog maintenance](docs/GRAPH_CATALOG.md) for pinned official sources and
regeneration. Source URLs belong in maintainer documentation, outside agent context.

```powershell
python -m unittest discover -s tests -v
npm --prefix src/frontend run build
```

The focused checks use synthetic data, a mocked SDK transport, and an isolated
database; they do not load `.env` or contact a tenant/model provider. Live tenant
queries and Teams message delivery still need validation in your configured tenant.

## Attribution

Netra builds on Fctr's Tako AI Agent; Microsoft metadata attribution is in
[third-party notices](THIRD_PARTY_NOTICES.md). The inherited licensing terms remain in
[LICENSE](LICENSE) pending the Netra license decision. Private migration notes,
source snapshots, and archived original files live in ignored `DO_NOT_SHARE/` and are
excluded from Docker builds.
