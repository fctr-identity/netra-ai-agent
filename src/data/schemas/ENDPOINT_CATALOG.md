# Netra endpoint catalog

Runtime inputs are `graph_get_endpoints.json` and `graph_read_operations.json`.
They describe the supported read-only Graph subset and contain no documentation
URLs. Response fields and interpretation are documented in endpoint notes; the
adapter uses a small collection/object flag. There is no separate response-schema
file. Reviewed descriptions and notes are maintained
in `scripts/graph_catalog_notes.py`; structural data comes from pinned Microsoft
metadata. See `docs/GRAPH_CATALOG.md` for the regeneration process.
