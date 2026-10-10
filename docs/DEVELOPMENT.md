# Development and checks

See [catalog maintenance](GRAPH_CATALOG.md) for pinned official sources and
regeneration. Source URLs belong in maintainer documentation, outside agent context.

```powershell
uv run python -m unittest discover -s tests -v
npm.cmd --prefix src/frontend run build
```

The focused checks use synthetic data, a mocked SDK transport, and an isolated
database; they do not load `.env` or contact a tenant/model provider. Live tenant
queries and Teams message delivery still need validation in your configured tenant.
