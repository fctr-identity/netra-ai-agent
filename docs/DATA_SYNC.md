# Data sync and CLI queries

Click **Data sync → Sync now**, or run the same snapshot engine once:

```powershell
uv run scripts/sync_entra_to_db.py
```

The CLI exits 0 for a complete sync and nonzero for partial/failing runs. There
is no built-in scheduler. Run this command from the repository root, or use the
virtual environment's Python with an absolute script path from cron or Windows
Task Scheduler when needed. An OS lock coordinates CLI and
UI syncs. A stale process history does not prevent a fresh UI sync.

### What Netra syncs

Sync copies the following directory data into local SQLite for fast queries and
joins. **Default** describes the shipped configuration; required Graph permissions
and tenant licensing still apply.

| Data | Details saved | Default | Notes |
| --- | --- | --- | --- |
| **Users** | Object ID, display/first/last names, sign-in name, email, enabled status, Member/Guest type, department, job title, employee ID, creation time, and configured custom attributes. | On | Manager relationships and password settings are not part of the standard user snapshot. |
| **Groups** | Object ID, name, description, email, security/mail-enabled flags, group types, membership rule, and role-assignable flag. | On | Memberships are stored separately. |
| **Group memberships** | Group ID, member ID, member object type, display name when available, and a limited-information flag. | On | Direct memberships; no precomputed transitive membership. The current v1.0 source omits service-principal members. |
| **Enterprise apps (service principals)** | Object ID, name, application/client ID, service-principal type, enabled status, assignment-required flag, and app-role definitions. | On | Represents applications and service identities in this tenant. |
| **App registrations** | Object ID, name, application/client ID, sign-in audience, and app-role definitions. | On | Application definitions, separate from enterprise apps. |
| **App assignments** | Assignment ID, target enterprise-app ID, assigned user/group/service-principal ID and type, principal name, app-role ID, and creation time. | On | Supports assignment joins; assignments alone do not establish effective access. Group-based app assignments apply to direct members, not nested-group members. |
| **MFA registrations** | User ID/name/sign-in name, MFA registered/capable flags, passwordless-capable flag, registered method types, and report update time. | On | User registration records, not sign-in events or proof that MFA is enforced. Missing records mean unknown. Disable with `SYNC_MFA_REGISTRATION=false`. |
| **Directory role definitions** | Role definition ID, name, description, and built-in flag. | Off | Enable with `SYNC_DIRECTORY_ROLES=true`. These are Entra administrator roles, separate from app roles. |
| **Directory role assignments** | Assignment ID, principal ID, role definition ID, directory scope, and app scope. | Off | Enabled with directory role definitions. Current assignments; PIM eligibility and assignment history are not synced. |
| **Conditional Access policies** | Policy ID, name, state, conditions, grant controls, and session controls. | Off | Enable with `SYNC_CONDITIONAL_ACCESS=true`. Stores configuration; does not simulate sign-in decisions. |
| **Devices** | Directory object ID, device ID, name, enabled status, operating system/version, trust type, and managed/compliant flags. | Off | Enable with `SYNC_DEVICES=true`. Entra directory inventory, not an Intune device-management snapshot. |

Directory records also retain the Graph JSON returned by their sync requests and
the local sync timestamp. This is the response to the selected request, not a copy
of every Graph property or relationship. Resource-level metadata records counts,
last attempts, last successful refreshes, and errors.

Sign-in and directory audit events are queried live with an explicit time lower
bound; they are not synced. Other supported relationships, such as a user's
direct reports, are retrieved live when needed. See the
[endpoint inventory](SUPPORTED_GRAPH_READS.md) for live and snapshot coverage.

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
