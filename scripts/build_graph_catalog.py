"""Build local read catalogs from a pinned official snapshot and reviewed notes.

Usage: python scripts/build_graph_catalog.py --source path/to/openapi.yaml
No downloads occur here or during agent runtime. Install requirements-dev.txt.
"""
import argparse
import json
import re
from pathlib import Path
import yaml
from graph_catalog_notes import RESOURCES, OPERATIONS, MEMBERSHIPS, REVISION, REVIEWED

ROOT = Path(__file__).resolve().parents[1]


def clean(value):
    if isinstance(value, str):
        value = re.sub(r'\[([^\]]+)\]\([^)]*\)', r'\1', value)
        return re.sub(r'(?:https?://|www\.)[^\s<>\"\)]+', '[external reference omitted]', value)
    if isinstance(value, list):
        return [clean(item) for item in value]
    if isinstance(value, dict):
        return {key: clean(item) for key, item in value.items() if key not in {'externalDocs', 'example', 'examples', 'xml'}}
    return value


def build(source, output):
    spec = yaml.load(source.read_text(encoding='utf-8-sig'), Loader=yaml.CSafeLoader)

    def deref(value):
        if '$ref' not in value:
            return value
        ref = value['$ref']
        if not ref.startswith('#/'):
            raise ValueError('External reference needs an explicit maintainer resolution: ' + ref)
        result = spec
        for part in ref[2:].split('/'):
            result = result[part.replace('~1', '/').replace('~0', '~')]
        return result

    normalized = {re.sub(r'\{[^}]+\}', '{}', path): (path, item) for path, item in spec['paths'].items()}
    endpoints, sources = [], []
    operations = list(OPERATIONS)
    for entity, operation, path, source_page, transitive in MEMBERSHIPS:
        operations.append((entity, operation, path, '$select $filter $search $count $top'))

    for entity, operation, path, query in operations:
        config = dict(RESOURCES[entity])
        membership = next((item for item in MEMBERSHIPS if item[0:2] == (entity, operation)), None)
        if membership:
            config.update(type='directoryObject' if entity == 'group' else 'group', source=membership[3])
            config['fields'] = 'id displayName' if entity == 'group' else 'id displayName description groupTypes'
            config['description'] = ('Transitive' if membership[4] else 'Direct') + (' members of one group.' if entity == 'group' else ' group memberships of one user.')
            config['interpretation'] = 'Preserve object id and @odata.type. Different member object types cannot all be treated as users. Transitive reads flatten nested membership; direct reads retain only immediate relationships. Group membership alone does not establish app assignments or successful access. Permission-limited members may contain only id/type; keep those objects and mark unknown properties.'
            config['retrieval'] = 'Resolve the parent id only when unknown. Advanced membership queries require ConsistencyLevel eventual and $count=true; the adapter supplies these headers. Hidden memberships require Member.Read.Hidden. The v1.0 direct members endpoint has a documented service-principal omission; Netra reports this limitation and does not silently call beta. Do not call a partial membership inventory complete for service-principal questions. Nested membership does not confer group-based enterprise app assignment.'
            config['permission'] = 'GroupMember.Read.All' if entity == 'group' else 'User.Read.All'
        # Microsoft's OpenAPI uses the graph alias for fully qualified casts.
        source_key = re.sub(r'\{[^}]+\}', '{}', path).replace('/microsoft.graph.', '/graph.')
        upstream_path, path_item = normalized[source_key]
        upstream = path_item['get']
        parameters = [deref(item) for item in path_item.get('parameters', []) + upstream.get('parameters', [])]
        available = {item['name'] for item in parameters if item.get('in') == 'query'}
        allowed = query.split()
        if set(allowed) - available:
            raise ValueError(f'{path}: unlisted upstream parameters {set(allowed) - available}')
        key = f'{entity}.{operation}'
        wanted = config['fields'].split()
        collection = operation != 'get'
        required = re.findall(r'\{([^}]+)\}', path)
        parameter_lines = [f'* {name} (path, required): Graph object id of the named parent; use a known id directly.' for name in required]
        for parameter in parameters:
            if parameter.get('in') == 'query' and parameter['name'] in allowed:
                parameter_lines.append(f"* {parameter['name']} (query, optional): {clean(parameter.get('description', 'Use the documented Graph query syntax.'))}")
        interpretation = config['interpretation']
        if operation == 'get':
            interpretation = 'Retrieve the already identified object. Do not repeat its list lookup when its id is known. ' + interpretation
        notes = '\n'.join(['## Parameters', *parameter_lines, '', '## Response',
            f"* JSON {'collection' if collection else 'object'} of {config['type']}. Useful fields: {', '.join(wanted)}.",
            f"* Successful reads return status=success, data={'list' if collection else 'object'}, complete=boolean. Graph wire collections use a value array; single-object reads return the object directly.",
            '* The adapter consumes value/continuation metadata and returns data with unchanged Graph field names. A sample is not a complete inventory. Omitted fields remain unknown.',
            '* Failed reads return status=error, error=message, error_code=code, http_status=number or null, complete=false. Never interpret a failure as empty data.',
            '', '## Interpretation and Related Data', interpretation, '', '## Retrieval Notes',
            f"* Application permission: {config['permission']}. Availability still depends on tenant features and consent.", config['retrieval'],
            '* Page size is not a total count. The adapter handles paging. Check status and complete; preserve errors rather than returning an empty list.',
            '* OData string literals escape an apostrophe by doubling it. Pass parameters separately; do not construct an absolute URL. Keep all requests read only.'])
        endpoint = {'id': key, 'entity': entity, 'operation': operation, 'name': f"{operation.replace('_', ' ').title()} {entity.replace('_', ' ')}",
            'method': 'GET', 'url_pattern': path, 'description': config['description'],
            'parameters': {'required': required, 'optional': allowed}, 'depends_on': [],
            'application_permissions': [config['permission']], 'notes': clean(notes),
            'response': {'collection': collection}, 'advanced_query': entity in {'user', 'group', 'device', 'application', 'service_principal'}}
        endpoints.append(endpoint)
        sources.append({'operation': key, 'upstream_path': upstream_path, 'operation_id': upstream['operationId'],
                        'documentation': f"https://learn.microsoft.com/en-us/graph/api/{config['source']}?view=graph-rest-1.0"})

    output.mkdir(parents=True, exist_ok=True)
    catalog = {'version': 'netra-graph-v1', 'entity_summary': sorted({entry['entity'] for entry in endpoints}), 'endpoints': endpoints}
    for name, payload in [('graph_get_endpoints.json', catalog),
                          ('graph_read_operations.json', {'operations': [entry['id'] for entry in endpoints]})]:
        content = json.dumps(clean(payload), ensure_ascii=False, indent=2) + '\n'
        if re.search(r'https?://|www\.', content):
            raise ValueError('External link in generated catalog')
        (output / name).write_text(content, encoding='utf-8')
    provenance = ROOT / 'docs/graph_catalog_sources.json'
    provenance.parent.mkdir(exist_ok=True)
    provenance.write_text(json.dumps({'revision': REVISION, 'reviewed': REVIEWED,
        'source': f'https://github.com/microsoftgraph/msgraph-metadata/blob/{REVISION}/openapi/v1.0/openapi.yaml',
        'license': 'MIT; see THIRD_PARTY_NOTICES.md', 'operations': sources}, indent=2) + '\n', encoding='utf-8')
    print(f'Generated {len(endpoints)} supported GET operations and response descriptions.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--output', type=Path, default=ROOT / 'src/data/schemas')
    args = parser.parse_args()
    build(args.source, args.output)
