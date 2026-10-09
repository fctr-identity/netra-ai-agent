# Maintaining the Graph read catalog

The committed runtime files are:

- `src/data/schemas/graph_read_operations.json`: small routing index.
- `src/data/schemas/graph_get_endpoints.json`: approved GET paths, parameters,
  descriptions, permissions, dependencies, and reviewed notes. Response fields,
  wrappers, and interpretation live in those notes. A small `response.collection`
  flag lets the adapter distinguish collections from single objects.

The initial catalog contains 25 operations for the POC scope. It is intentionally
an allowlist, not every Graph GET endpoint. Calls outside it fail in the adapter.

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
