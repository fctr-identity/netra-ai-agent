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

Use [uv](https://docs.astral.sh/uv/getting-started/installation/) and Node.js 24.
Netra uses uv with its existing requirements files. From the repository root,
create a Python 3.12 environment once; skip this command if `.venv` already exists:

```powershell
uv venv --python 3.12
```

Install the backend dependencies and build the UI (Windows PowerShell):

```powershell
uv pip install -r requirements.txt
npm.cmd --prefix src/frontend ci
npm.cmd --prefix src/frontend run build
```

No virtual environment activation is needed. On macOS/Linux, use `npm` instead
of `npm.cmd`; the uv commands are the same. If you do not already have a private
`.env`, copy `.env.example` to `.env` (`Copy-Item .env.example .env` in PowerShell,
or `cp .env.example .env` on macOS/Linux). Keep existing configuration when
repeating setup. Configure Entra and a model provider below before starting Netra.

### Entra app registration

Netra uses application credentials for Microsoft Graph and keeps its own local
admin login. **No callback/redirect URI or Entra single sign-on configuration is
needed for this version.** Create the identity through **App registrations**;
Entra creates its matching Enterprise Application (service principal) automatically.
See Microsoft's [app registration guide](https://learn.microsoft.com/en-us/entra/identity-platform/quickstart-register-app)
and [client credentials flow](https://learn.microsoft.com/en-us/entra/identity-platform/v2-oauth2-client-creds-grant-flow).

1. In the [Microsoft Entra admin center](https://entra.microsoft.com), choose the
   intended tenant, then **Entra ID → App registrations → New registration**.
   Name it **Netra**, select **Single tenant only** (accounts in this organizational
   directory only), and leave the optional redirect URI blank. Select **Register**.
2. On **Overview**, copy the **Directory (tenant) ID** and **Application (client) ID**.
   Use the application/client ID, not either object's Object ID.
3. Open **Certificates & secrets → Client secrets → New client secret**. Enter a
   description and expiry, then copy the secret **Value** immediately. Entra only
   shows it once; the Secret ID is not a credential. See
   [Microsoft's credential instructions](https://learn.microsoft.com/en-us/entra/identity-platform/how-to-add-credentials).
4. Open **API permissions → Add a permission → Microsoft Graph → Application
   permissions**. Add the four permissions used by the default sync below. Add the
   optional permissions only for features you want to use. An automatically added
   delegated `User.Read` permission can be removed; Netra uses application permissions.

| Read scope | Microsoft Graph application permissions |
| --- | --- |
| Users, groups, direct memberships; Teams group authorization | `User.Read.All`, `Group.Read.All` |
| Enterprise apps, app registrations, resource-side app-role assignments and owners | `Application.Read.All` |
| MFA registration reports, sign-in and directory audit reads | `AuditLog.Read.All` |
| Optional directory role definitions and assignments | `RoleManagement.Read.Directory` |
| Optional Conditional Access policies | `Policy.Read.All` |
| Optional directory device inventory and registered owners/users | `Device.Read.All` |
| Optional user/group app assignments and delegated consent grants | `Directory.Read.All` |
| Optional parent-group membership reads | `GroupMember.ReadBasic.All` (see endpoint notes and documented read alternatives) |
| Optional authentication strengths and authentication-method policy | `Policy.Read.AuthenticationMethod` (`Policy.Read.All` is a documented alternative) |
| Optional targeted user authentication-method inventory | `UserAuthenticationMethod.Read.All` |
| Optional administrative units and their members | `AdministrativeUnit.Read.All` |
| Optional tenant organization, domains, license SKUs | `Organization.Read.All`, `Domain.Read.All`, `LicenseAssignment.Read.All`, respectively |

Grant only the scopes you enable. Hidden group membership additionally needs
`Member.Read.Hidden`. Permission failures are reported as unavailable evidence,
not as empty data. Netra does not need Graph write permissions.

The expanded live-read catalog does not increase the default sync permission set.
See the [complete supported endpoint list](docs/SUPPORTED_GRAPH_READS.md) for each
operation's use, permission, availability, and sync coverage. New relationships,
tenant details, consent grants, and method policies are live reads in this version.

5. In **API permissions**, select **Grant admin consent** for your tenant and
   confirm that each requested application permission shows **Granted for** that
   tenant. Microsoft Graph application permission consent requires an authorized
   administrator, such as a **Privileged Role Administrator**. Being an app owner
   alone is insufficient. See [Microsoft's admin consent guide](https://learn.microsoft.com/en-us/entra/identity/enterprise-apps/grant-admin-consent).
6. Put the three values in the private `.env` in Netra's repository root:

   ```dotenv
   ENTRA_TENANT_ID=<directory-tenant-id>
   ENTRA_CLIENT_ID=<application-client-id>
   ENTRA_CLIENT_SECRET=<client-secret-value>
   ```

The SDK requests `https://graph.microsoft.com/.default` automatically. There is no
local redirect endpoint to register, API to expose, or user-assignment setup needed
for these app-only Graph reads. Optional directory roles, Conditional Access and
devices need their listed permission for live reads; set their corresponding
`SYNC_*` flags to `true` if they should also be copied into the database. The flags
are listed under **Sync and query** below. Restart Netra after configuration changes.

Configure a model provider separately. The template defaults to
`AI_PROVIDER=openai_compatible`; set its base URL, token, reasoning model, and
coding model in the same private `.env`:

```dotenv
AI_PROVIDER=openai_compatible
OPENAI_COMPATIBLE_BASE_URL=<provider-api-base-url>
OPENAI_COMPATIBLE_TOKEN=<provider-api-key>
OPENAI_COMPATIBLE_REASONING_MODEL=<model-id>
OPENAI_COMPATIBLE_CODING_MODEL=<model-id>
```

The two model IDs can be the same. Inherited provider adapters also support `openai`, `azure_openai`,
`google`, `vertex_ai`, `anthropic`, and `bedrock`. The template includes the
OpenAI and Azure alternatives. Choose models supporting structured tool calls.

Start the local server:

```powershell
uv run main.py
```

Open **http://127.0.0.1:8001**. The first start prints a one-time setup token in
the terminal; use it to create the local admin login. Entra credentials are for
directory reads and do not replace that login. The default server binds to
loopback. For a public HTTPS deployment, configure the proxy and set
`COOKIE_SECURE=true`. Use one API worker and one replica.

## Sync and query

Click **Data sync → Sync now**, or run the same snapshot engine once:

```powershell
uv run scripts/sync_entra_to_db.py
```

The CLI exits 0 for a complete sync and nonzero for partial/failing runs. There
is no built-in scheduler. Run this command from the repository root, or use the
virtual environment's Python with an absolute script path from cron or Windows
Task Scheduler when needed. An OS lock coordinates CLI and
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

### Ask from the terminal

The CLI uses the same agent workflow and Entra/model configuration as the UI:

```powershell
uv run scripts/netra-cli.py "Use live Graph to list five users and their account-enabled status"
uv run scripts/netra-cli.py --interactive
uv run scripts/netra-cli.py --help
```

Tabular answers are saved as CSVs; the CLI prints the output path and a short
preview. Use `--session-id <name>` to group related questions, or `--scriptonly`
to generate the final retrieval script without executing it. Discovery may still
make read-only Graph calls in script-only mode. Exported retrieval scripts depend
on this Netra checkout and its configured virtual environment.

## Teams

Teams is optional and uses the same query runtime. Install its dependencies with
`uv pip install -r requirements.txt -r requirements-teams.txt`, configure the bot
identity and allowed groups, and follow [the Teams guide](src/integrations/teams/README.md). Bot Service needs a
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
contracts for **53 approved GET operations**, not the entire Microsoft Graph API.
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

Generated API discovery, SQL discovery, and saved-result analysis run in local
child processes. The shared supervisor also covers final UI, CLI, Teams, and
saved-procedure retrieval scripts. Graph operations default to 90 seconds.
API discovery and final retrieval execution allow at least 120 seconds, or the
configured `GRAPH_TIMEOUT_SECONDS` plus 30 seconds when that is longer. These are
whole-script deadlines, including worker startup; a script with several slow
operations can still reach its limit. Analysis retains a 60-second deadline and
SQL discovery a 15-second deadline. Captured output is capped at 8 MiB stdout and 1 MiB stderr;
oversized output fails rather than returning truncated success. Cancellation is
checked independently of progress messages, and children are killed and reaped
on failure/cancellation. These are time/output bounds, not memory/CPU quotas or
filesystem/credential isolation.

While a query runs, the activity panel shows its current phase or Graph operation,
elapsed time, and a slow-operation notice after 20 seconds. Completed requests and
retry/timeout states remain in expandable activity; Stop cancels the running work.
Progress events carry only fixed phase/tool labels, catalog operation labels,
correlation IDs, status, elapsed time, and optional retry timing. Model reasoning,
tenant records, raw URLs, headers, and error bodies are excluded from this feed.
The existing result, optional generated-script, and token-usage events serve their
separate UI views. Per-attempt HTTP timing/status diagnostics stay in server logs;
they omit request URLs, credentials, and response bodies. Timers update locally
without per-second server events.

Graph 429s and AI provider throttling appear as rate-limit status in query activity
and the CLI. Model status covers planning, discovery, review, and synthesis through
the shared model boundary. A countdown displays the provider's `Retry-After` hint
(seconds or HTTP date; millisecond hints are also accepted). Without a valid hint,
the UI shows rate limiting without inventing a countdown. This is a requested
retry delay, not a guaranteed quota reset. Existing SDK retries and query deadlines
remain unchanged; completion, failure, or cancellation clears the waiting state.
Only throttled model calls add activity entries, keeping normal progress compact.

API discovery retains each returned test payload and its exact tested code in a
temporary folder under the current turn's artifacts. The model receives a valid,
bounded JSON preview and a test ID; `save_artifact` promotes that ID's original
payload and code into the existing durable artifact/result-set storage. The
model does not copy response JSON back into the save call. `inspect_test_result`
can preview a nested value locally without repeating a Graph request.

Temporary test folders are removed when discovery finishes, fails, or is
cancelled. After an abrupt process exit, the next web, CLI, or integration query
sweeps abandoned test folders with no changes in the last 24 hours. This is
opportunistic cleanup, not a timer. Selected artifacts remain with the conversation
and follow its existing retention; CLI evaluation output is still retained in
its chosen runtime directory. No new storage service is required.

Assignments are not effective access. MFA registration is not successful MFA use.
Direct and transitive memberships differ, and nested groups do not confer
group-based app assignments. The v1.0 group-members source has a documented
service-principal omission; Netra records that limit. PIM eligibility, risk
analysis, Intune management, and write operations are outside this release.

## Catalog maintenance and checks

See [catalog maintenance](docs/GRAPH_CATALOG.md) for pinned official sources and
regeneration. Source URLs belong in maintainer documentation, outside agent context.

```powershell
uv run python -m unittest discover -s tests -v
npm.cmd --prefix src/frontend run build
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
