# Installation and Entra setup

For the published Docker image, follow the [README quick start](../README.md#quick-start-docker).
The steps below cover manual installation with uv. Source builds are covered in
the [Docker section](#docker).

Use [uv](https://docs.astral.sh/uv/getting-started/installation/) and Node.js 24.
Clone the beta release and enter its directory:

```bash
git clone --branch v0.1.0-beta.1 https://github.com/fctr-identity/netra-ai-agent.git
cd netra-ai-agent
```

Netra uses uv with its existing requirements files. Create a Python 3.12 environment
once; skip this command if `.venv` already exists:

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
See the [complete supported endpoint list](SUPPORTED_GRAPH_READS.md) for each
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
are listed in the [sync guide](DATA_SYNC.md#what-netra-syncs). Restart Netra after configuration changes.

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

## Docker

The Docker Hub repository is
[fctrid/netra-ai-agent-for-entra](https://hub.docker.com/r/fctrid/netra-ai-agent-for-entra).
The first beta image is `fctrid/netra-ai-agent-for-entra:0.1.0-beta.1` for Linux
AMD64. The `beta` tag follows the most recently published beta; the default Compose
file pins a version so updates are deliberate. Docker Desktop runs the Linux image
on supported Windows and macOS hosts; this release does not publish a native ARM64 image.

After configuring `.env`, run `docker compose pull` and `docker compose up -d`.
Netra is exposed on loopback port 8001, with named volumes for the database and
chat artifacts. The published image includes the optional Teams dependencies;
Teams remains disabled until configured and enabled. Use
`docker compose exec netra python scripts/sync_entra_to_db.py` for a one-shot sync.

To build your own image from the checked-out source:

```bash
docker compose -f docker-compose.build.yml up --build -d
```

The source build excludes Teams dependencies by default. Set `INSTALL_TEAMS_BOT=true`
in your configuration before building if you need them. Use the same
`-f docker-compose.build.yml` option for subsequent source-container commands.

To upgrade the published image, update the pinned tag in `docker-compose.yml`,
then run `docker compose pull` and `docker compose up -d`. Back up your data first.
Keep the named volumes; `docker compose down -v` deletes them.

## Teams

Teams is optional and uses the same query runtime. Install its dependencies with
`uv pip install -r requirements.txt -r requirements-teams.txt`, configure the bot
identity and allowed groups, and follow [the Teams guide](../src/integrations/teams/README.md). Bot Service needs a
reachable HTTPS messaging endpoint even when the Netra process runs locally.
The bot tenant must match `ENTRA_TENANT_ID`; authorization checks use Netra's
read-only Graph identity. Slack and specialized access analyses are outside this POC.
