# Administrator question library

[Documentation guide](README.md) · [Supported endpoints and permissions](SUPPORTED_GRAPH_READS.md)

These suggested questions are grounded in Netra's implemented catalog. They are
not a list of passed live tests. The ten UI starters are adapted from the CLI
evaluation scenarios; this library broadens the administrator use cases.

**Simple** means a focused lookup or small inventory. **Advanced** means comparing
relationships, combining sources, or interpreting policy or event evidence.
These labels do not predict response time. A tenant-wide Simple lookup can cost
more than an Advanced investigation of one user.

Replace text in square brackets with your own identifiers or values before
submitting. If a name is ambiguous, ask Netra to show matching objects first.

## Adapt a question to your tenant

| Goal | How to ask |
| --- | --- |
| Quick start in any tenant | “Show a sample of up to five…” State that the result is a sample. |
| Targeted investigation | Name one user, group, application, device, department, or administrative unit. Bound related results. |
| Broader inventory | Identify the population and request a summary first. Ask whether every required page was retrieved and which fields were unavailable. |
| Large population or repeated report | Use a recent local snapshot where its fields and relationships are supported. Split live investigations by a meaningful population or time window. |
| Recent activity | State the time range and timezone. Start with 24 hours and a small event sample, then narrow by user/app/activity before expanding. |

For a complete report, add: “Retrieve all pages needed for this population. If a
limit, timeout, permission failure, or missing field prevents completion, label
the report partial and state what is missing. Do not turn a sample into a total.”
This expresses the reporting goal; it does not bypass Netra's execution limits.
Large-tenant capacity is not established. Avoid starting with every user joined
to every group, app, and event in one query.

## Users and organizational attributes

Uses user list/detail, direct reports, and selected properties.

| Level | Example question |
| --- | --- |
| Simple | Show a sample of up to five users with their display name, sign-in name, user type, and account-enabled status. |
| Simple | Show up to 25 disabled users in department [department], with names and sign-in names. State whether this is a sample. |
| Simple | Show up to 25 guest accounts with their creation time and enabled status. Do not infer recent activity from creation time. |
| Simple | Show the directory profile and selected organizational attributes for user [user ID or sign-in name]. |
| Advanced | Summarize users in department [department] by member/guest and enabled/disabled status. Use the latest local snapshot if those fields are available, state freshness, and distinguish complete counts from samples. |
| Advanced | Show up to 25 direct reports for manager [user ID], preserving user/contact types. Do not treat this as the full reporting hierarchy. |

## Groups and membership

Uses group list/detail, direct/transitive members, owners, parent memberships,
and user direct/transitive group memberships.

| Level | Example question |
| --- | --- |
| Simple | List up to ten groups with their names, security/mail flags, and group types. |
| Simple | Show the configuration and returned owners of group [group ID]. State any owner-visibility limitation. |
| Advanced | For group [group ID], compare up to 25 direct and transitive members by name and object type. Explain nesting visible in the samples without claiming a total. |
| Advanced | For user [user ID], compare up to 25 direct and transitive group memberships. Distinguish direct memberships from those visible only through nesting. |
| Advanced | Show direct and transitive parent memberships for group [group ID], preserving group and administrative-unit types where returned. |
| Advanced | Using the current local snapshot, find groups with more than [member count] recorded direct members. State the snapshot time and documented membership-type omissions; do not claim these are complete Graph counts. |

The v1.0 direct-member and group-owner visibility limitations remain relevant even
when pagination completes. See endpoint notes. Nested membership alone does not
confer group-based enterprise-app assignments.

## Directory devices

Uses device list/detail and device-side registered owners/users. This is Entra
directory inventory, not Intune management or primary-user data.

| Level | Example question |
| --- | --- |
| Simple | Show up to five devices with name, operating system, enabled, managed, and compliance status. For the first device, show its approximate last sign-in time. Preserve unknown values. |
| Simple | Show up to 25 disabled directory devices, including operating system and trust type where available. |
| Advanced | For device [device ID], compare its registered owners and registered users. Resolve returned names without calling them Intune primary users. |
| Advanced | Among up to 25 devices running [operating system], show which report an approximate last sign-in before [UTC date]. Separate missing timestamps and describe these as review candidates, not proof of inactivity. |

## Enterprise apps, registrations, and consent

Uses application/service-principal list/detail/owners, resource-side assignments,
user/group assignments, client application permissions, and delegated consent grants.

| Level | Example question |
| --- | --- |
| Simple | List up to five enterprise applications with name, application ID, and enabled status. For the first app, show its type and whether assignment is required. |
| Simple | List up to five app registrations with name, application ID, and sign-in audience. Show the first registration's creation time. |
| Advanced | For app registration [object ID], find its corresponding enterprise application by application ID and compare the owners returned for each object. |
| Advanced | Show up to 25 assignments to enterprise app [service principal ID], separating users, groups, and service principals and resolving app-role names where possible. |
| Advanced | Show app-role assignments for user [user ID] and group [group ID]. Preserve assignment principal/source information and distinguish configured assignment from effective access. |
| Advanced | For client enterprise app [service principal ID], list granted application permissions and delegated consent scopes. Resolve resource names, distinguish app-only from delegated permissions, and state whether consent is tenant-wide or user-specific. |
| Advanced | For up to ten app registrations, list credential metadata expiring within 30 days: app name, credential name or key ID, type, and expiry. Omit public key bytes and secret values; do not infer expiry from app creation time. |
| Advanced | Choose one enabled member user, compare up to ten direct/transitive groups, and inspect assignments for up to five enterprise apps. Identify direct and direct-group assignments, not nested-group access. State the five-app sample scope and missing evidence. |

An application that does not require assignment is not proof that every user has
effective access. Credential metadata is a live read and is not in the current
application snapshots; keep those reads bounded.

## MFA registration and authentication methods

Uses the registration report, targeted per-user method inventory, and tenant
authentication-method policy. Check optional permissions before targeted reads.

| Level | Example question |
| --- | --- |
| Simple | Show up to ten registration-report rows with user name, MFA registration, and MFA capability status. State report freshness limitations. |
| Advanced | For up to ten enabled users, join current user details to the registration report by user ID. Show whether a report row was found and preserve unknown values. |
| Advanced | For user [user ID], list registered authentication-method types without phone numbers or other method details that are unnecessary for the question. Compare with the registration report if available. |
| Advanced | Summarize the tenant authentication-method policy: enabled methods, included/excluded targets, and registration enforcement where returned. Distinguish configuration from actual registration or use. |

Missing report rows are unknown, not evidence of being unregistered. Registration
and capability do not establish successful MFA use or effective enforcement.

## Conditional Access

Uses policy list/detail, named locations, and authentication strengths.

| Level | Example question |
| --- | --- |
| Simple | List up to ten Conditional Access policies with their names and enabled, disabled, or report-only states. |
| Advanced | For policy [policy ID], summarize included/excluded users, groups, apps, conditions, and grant controls. Resolve referenced names where supported. |
| Advanced | For policy [policy ID], resolve its referenced named locations and authentication strength, including allowed method combinations. Preserve unknown references. |
| Advanced | Review configured policies for application [application ID]. Explain explicit and broad application targeting and exclusions; do not present this as a simulation of effective access. |

Policy configuration, user registration, and observed sign-in outcomes are
different evidence. Netra does not run a Conditional Access What If simulation.

## Roles and administrative units

Uses role definitions, current role assignments, administrative units, and unit members.

| Level | Example question |
| --- | --- |
| Simple | Show the role definition and named permissions for directory role [role name or ID]. |
| Advanced | Find Global Administrator and show up to ten current role assignments, resolving principal names and types where possible and including assignment scope. |
| Advanced | For administrative unit [unit ID], show its configuration, up to 25 members, and current directory role assignments scoped to that unit. |
| Advanced | Compare current assignments for directory roles [role A] and [role B]. Separate tenant-wide and administrative-unit scopes and identify shared principals. State completeness. |

These are current assignments, not PIM eligibility or historical access. A group
principal should not be silently converted into a complete list of effective admins.

## Sign-ins and directory audit activity

Uses sign-in and audit list/detail. These are live reads with bounded time windows;
availability depends on permission, licensing, and retained events.

| Level | Example question |
| --- | --- |
| Simple | Show up to ten failed sign-ins in the last 24 hours with time, user, app, and failure reason. State the UTC window and keep missing fields unknown. |
| Advanced | For user [user ID], show up to 25 sign-ins between [UTC start] and [UTC end]. Summarize returned outcomes and inspect the first failed event's detail if one exists. |
| Advanced | For the last 24 hours, show up to five sign-ins and five directory audit events, then inspect the first event of each type. Keep the types separate and summarize time, actor, app/activity, status, and failure reason. State the UTC window. |
| Advanced | For [UTC start] through [UTC end], summarize up to 25 directory audit events concerning [target object ID]. Show actor, activity, result, and reported modified properties where available. Do not infer causation from nearby sign-ins. |

“No events” is different from access being denied, retention excluding the window,
or a request failing. A sampled event list does not establish a failure rate for
the whole tenant or prove that an account has never been used.

## Tenant, domains, and licensing

Uses organization/domain/SKU list/detail and selected user license properties.

| Level | Example question |
| --- | --- |
| Simple | Show the tenant organization name, verified domains, and directory-sync status and timestamp where reported. |
| Simple | List configured domains with verification, default-domain, and authentication-type properties. |
| Simple | List subscribed license SKUs, enabled capacity, consumed units, and warning/suspended capacity. Keep service-reported values distinct. |
| Advanced | For user [user ID], map assigned license SKU IDs to subscribed SKU names and show reported service-plan and license-assignment states. Do not assume a license guarantees effective access. |
| Advanced | For up to 25 users in department [department], show reported license-assignment errors and direct/group assignment sources. Keep missing assignment states unknown and state sample coverage. |

User licensing questions use selected user properties and subscribed SKUs. The
separate user `licenseDetails` path is outside this app-only catalog. Reported
capacity is not an invoice or a guaranteed count of immediately assignable seats.

## Custom attributes

Uses selected user properties and the configured snapshot attribute set.

| Level | Example question |
| --- | --- |
| Simple | For user [user ID], show [configured directory/schema extension or on-premises extension attribute] and distinguish a missing value from an unavailable field. |
| Advanced | Using the latest local snapshot, summarize users by [configured custom attribute] and enabled status. Include missing values as a separate category, state freshness, and identify whether the attribute was configured for sync. |

Specify exact supported property names and configure snapshot attributes as
described in [Data sync and CLI](DATA_SYNC.md). Open extensions and
custom security attributes are not advertised as supported by this library.

## Coverage and interpretation

The [generated inventory](SUPPORTED_GRAPH_READS.md) lists every supported GET path,
its selected application permissions, availability, and sync coverage. Additional
live endpoints do not automatically add snapshot fields or tables. The
[catalog guide](GRAPH_CATALOG.md) records deliberate exclusions, including beta,
delegated-only reads, Intune, PIM/risk/governance, and unrelated Microsoft 365
workloads. Query breadth and tenant size do not expand that catalog.

When sharing results, retain the data source, snapshot/time window, sample limits,
and any incomplete retrieval. The library can grow with reviewed endpoint additions
and new administrator scenarios without adding every question to the home screen.
