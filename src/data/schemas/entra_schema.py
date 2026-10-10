"""Model-visible schema and interpretation generated from the actual directory tables."""
def get_entra_database_schema():
    from src.core.entra.sync.models import (User, Group, GroupMembership, ServicePrincipal, Application, AppRoleAssignment,
        MFARegistration, DirectoryRole, RoleAssignment, ConditionalAccessPolicy, Device, DirectorySnapshot)
    from src.config.settings import settings
    models = (User, Group, GroupMembership, ServicePrincipal, Application, AppRoleAssignment, MFARegistration,
              DirectoryRole, RoleAssignment, ConditionalAccessPolicy, Device, DirectorySnapshot)
    sections = ['Microsoft Entra local directory snapshot. SQL is read only. IDs are Graph object identifiers stored as text.']
    sections.append('Configured tenant_id for SQL filters: ' + settings.tenant_id)
    for model in models:
        sections.append('\nTABLE: ' + model.__tablename__ + '\n' + '\n'.join(
            f'- {column.name} ({column.type})' for column in model.__table__.columns))
    sections.append('''
Join group_memberships.group_id to groups.id and member_id to users.id only where member_type='user'.
GroupMembership records are direct edges. Transitive queries must deliberately traverse nested groups and avoid cycles.
The v1.0 members source omits service principals; do not claim complete service-principal membership coverage.
Enterprise applications are service_principals. Application registrations are applications; join their app_id fields.
app_role_assignments.resource_id references service_principals.id. principal_id can identify a User, Group or ServicePrincipal.
Preserve direct versus group grants. Group-based application assignments apply to direct users; nested membership does not grant them.
mfa_registrations.id references users.id. LEFT JOIN to retain users with no report, which means unknown, not unregistered.
is_mfa_registered is registration, is_mfa_capable is capability; neither establishes policy enforcement or successful MFA use.
Check directory_snapshots for every requested resource: last_successful_at, status, error, notes and record_count.
A missing snapshot is unavailable, not an empty population. A failed refresh retains prior rows with their old freshness.
A completed zero-row snapshot is a valid empty result. Optional roles/policies/devices may not have been synced.
All queries must be scoped to the configured tenant_id. Shared login/history/procedure tables are not directory query sources.
raw_json retains selected original Graph fields. Use json_extract for supported stored fields; missing JSON values are unknown.
Use custom_attributes only for configured selections; preserve missing values as null.
Custom attribute keys are the literal configured property names, including dots. Quote dotted keys in JSON paths instead of treating them as nested objects.
Events are live-only, absent from this schema.
''')
    sections.append('Configured custom user attributes: ' + ', '.join(settings.entra_user_custom_attributes_list or ['none']))
    return '\n'.join(sections)
