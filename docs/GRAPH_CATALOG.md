# Maintaining the Graph read catalog

The committed runtime files are:

- `src/data/schemas/graph_read_operations.json`: small routing index.
- `src/data/schemas/graph_get_endpoints.json`: approved GET paths, parameters,
  descriptions, permissions, dependencies, and reviewed notes. Response fields,
  wrappers, and interpretation live in those notes. A small `response.collection`
  flag lets the adapter distinguish collections from single objects.

The catalog contains 53 operations for common administrator questions. It is intentionally
an allowlist, not every Graph GET endpoint. Calls outside it fail in the adapter.

## Administrator-focused coverage

The October 9 scope correction supersedes the earlier request for every Entra
GET operation. Select common administrator questions first, then include the
list, detail, and relationship reads needed to answer them. Do not expand by
blindly importing every GET from OpenAPI or claim exhaustive administrator coverage.

The [generated endpoint inventory](SUPPORTED_GRAPH_READS.md) lists every path,
administrator use, selected read permission, feature availability, and sync status.
The expansion adds 28 operations to the original 25. All 53 paths and selected
query parameters are checked against pinned v1.0 metadata. Microsoft Learn
permission and interpretation review is recorded in the provenance file.
These are implemented catalog capabilities, not a claim of live tenant verification.

| Area | Implemented reads and interpretation |
| --- | --- |
| Users | List/detail, direct reports, direct/transitive group memberships, app assignments, targeted authentication methods; selected attributes and license properties |
| Groups | List/detail, direct/transitive members, owners, parent/transitive memberships, app assignments; group-owner omissions remain explicit |
| Devices | List/detail, registered owners and users; reverse matching supports user-to-device questions without assuming Intune primary-user semantics |
| Applications | Registrations and enterprise apps, their separate owners, resource-side assignments, client app permissions, delegated consent grants; credential expiry metadata through selected properties |
| Conditional Access | Policies, named locations, authentication strengths; configured targeting is not proof of a sign-in outcome |
| Authentication | Registration report, method policy with nested configurations, optional targeted per-user method inventory |
| Administrative access | Role definitions, assignments including detail, administrative units and their members; no PIM eligibility claim |
| Activity | Sign-in and audit list/detail with bounded time windows; retention and freshness remain explicit |
| Tenant/licensing | Organization, domains, subscribed SKUs and joins to selected user license properties |

For each added operation, publish its path, administrator use case, required
application permissions, licensing/availability, and live/sync support. An endpoint
is only advertised as supported after its runtime catalog and adapter checks are
in place. Keep permission-limited, not implemented, and empty results distinct.

New operations are live reads. Existing sync jobs and tables remain unchanged;
the inventory identifies exactly which selected data already has snapshots.
Adding a live endpoint does not automatically require a new synchronized table.
Delta operations are deferred until
incremental sync is needed. Beta, delegated-only operations, PIM/risk/governance,
Intune, and unrelated Microsoft 365 workloads are outside the initial expansion.

This grouping follows Microsoft's [Entra identity API overview](https://learn.microsoft.com/en-us/graph/identity-network-access-overview).
Microsoft's current permission tables mark application access unsupported for
[manager](https://learn.microsoft.com/en-us/graph/api/user-list-manager?view=graph-rest-1.0),
[licenseDetails](https://learn.microsoft.com/en-us/graph/api/user-list-licensedetails?view=graph-rest-1.0),
[user ownedDevices](https://learn.microsoft.com/en-us/graph/api/user-list-owneddevices?view=graph-rest-1.0),
and [user registeredDevices](https://learn.microsoft.com/en-us/graph/api/user-list-registereddevices?view=graph-rest-1.0).
Those exact paths are not admitted in this app-only catalog. This is a documented
support boundary, not a claim that calls were attempted and failed in this tenant.
Supported alternatives include directReports for an explicitly bounded inverse
reporting lookup, device-side registered-owner/user relationships, and selected
user license fields joined to subscribed SKUs. Alternatives retain their own
coverage and permissions rather than pretending to be identical endpoints.
These maintainer links never enter runtime agent context.

Authentication-context references, method-specific policy detail endpoints,
and other specialized policy relationships can be added later when an actual
administrator question needs them; this is deliberately a curated subset.

## Official sources

Structural metadata comes from Microsoft's
[v1.0 OpenAPI snapshot](https://github.com/microsoftgraph/msgraph-metadata/blob/15780e98e1082517bc7a39a6b75b356a085326d9/openapi/v1.0/openapi.yaml),
pinned at `15780e98e1082517bc7a39a6b75b356a085326d9`. Review provenance and Microsoft
Learn pages for each operation are recorded in `graph_catalog_sources.json`.
The source is development input only; it is not downloaded at runtime.

`scripts/graph_catalog_notes.py` owns the curated scope, permissions, useful fields,
and interpretation. Notes explain parameters, response wrappers,
identifier joins, direct/transitive semantics, availability, pagination, report
freshness, and limitations. These additions survive structural regeneration.
OpenAPI metadata alone is insufficient to explain those operational meanings.

To regenerate, save the pinned source locally and run:

```console
python -m pip install -r requirements-dev.txt
python scripts/build_graph_catalog.py --source PATH_TO_PINNED_OPENAPI_YAML
```

The generator resolves internal references and validates the selected GET
operations and query parameters against the source. Useful response fields come
from the reviewed resource notes.
It emits deterministic JSON without a separate response-schema file or recursive
type definitions. Inspect retrieved samples for nested fields when needed.
Runtime Graph values, particularly extensions, may add properties.
GET wire collections use `value` while EntraAPIClient exposes rows under `data`.

## Updating coverage

1. Add reviewed scope and notes in `graph_catalog_notes.py`, including applicable
   application permissions and how to distinguish missing evidence from empty data.
2. Check the operation against official v1.0 documentation and metadata. Exclude
   secret retrieval, write actions, unrelated workloads, and arbitrary URL access.
3. Regenerate and inspect both runtime JSON files and the provenance record. Keep operation IDs stable.
4. Update the sync/schema only if the resource needs local persistence.
5. Run the small offline checks and try the new read in a test tenant.

Runtime artifacts must contain no external documentation links, external schema
references, or examples containing service URLs. Maintainer provenance stays in
`docs/`; it is not injected into model context. A model wrapper also removes
hyperlinks from instructions, tool schemas, history, tool returns, and directory
values. Raw saved evidence is not rewritten by that projection.
