"""Small-tenant snapshot sync. Publish a resource only after all its reads succeed."""
import asyncio
import os
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from sqlalchemy import delete, select
from src.config.settings import settings
from src.core.entra.client import EntraAPIClient
from src.core.storage.operations import DatabaseOperations
from src.core.storage.models import SyncHistory, SyncStatus
from .models import (User, Group, GroupMembership, ServicePrincipal, Application, AppRoleAssignment,
                     MFARegistration, DirectoryRole, RoleAssignment, ConditionalAccessPolicy, Device, DirectorySnapshot)


def now():
    return datetime.now(timezone.utc)


@contextmanager
def sync_lock():
    """OS lock coordinates the local UI process with externally scheduled CLI runs."""
    path = Path(settings.DB_DIR) / 'netra-sync.lock'
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('a+b') as handle:
        handle.seek(0, os.SEEK_END)
        if not handle.tell():
            handle.write(b'0')
            handle.flush()
        handle.seek(0)
        try:
            if os.name == 'nt':
                import msvcrt
                msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as exc:
            raise RuntimeError('A directory sync is already running') from exc
        try:
            yield
        finally:
            handle.seek(0)
            if os.name == 'nt':
                msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


FIELDS = {
    User: {'user_principal_name': 'userPrincipalName', 'mail': 'mail', 'given_name': 'givenName', 'surname': 'surname',
           'account_enabled': 'accountEnabled', 'user_type': 'userType', 'department': 'department', 'job_title': 'jobTitle',
           'employee_id': 'employeeId', 'created_date_time': 'createdDateTime'},
    Group: {'description': 'description', 'mail': 'mail', 'security_enabled': 'securityEnabled', 'mail_enabled': 'mailEnabled',
            'group_types': 'groupTypes', 'membership_rule': 'membershipRule', 'is_assignable_to_role': 'isAssignableToRole'},
    ServicePrincipal: {'app_id': 'appId', 'service_principal_type': 'servicePrincipalType', 'account_enabled': 'accountEnabled',
                       'app_role_assignment_required': 'appRoleAssignmentRequired', 'app_roles': 'appRoles'},
    Application: {'app_id': 'appId', 'sign_in_audience': 'signInAudience', 'app_roles': 'appRoles'},
    AppRoleAssignment: {'resource_id': 'resourceId', 'principal_id': 'principalId', 'principal_type': 'principalType',
                        'principal_display_name': 'principalDisplayName', 'app_role_id': 'appRoleId', 'created_date_time': 'createdDateTime'},
    MFARegistration: {'user_principal_name': 'userPrincipalName', 'is_mfa_registered': 'isMfaRegistered',
                      'is_mfa_capable': 'isMfaCapable', 'is_passwordless_capable': 'isPasswordlessCapable',
                      'methods_registered': 'methodsRegistered', 'last_updated_date_time': 'lastUpdatedDateTime'},
    DirectoryRole: {'description': 'description', 'is_built_in': 'isBuiltIn'},
    RoleAssignment: {'principal_id': 'principalId', 'role_definition_id': 'roleDefinitionId', 'directory_scope_id': 'directoryScopeId', 'app_scope_id': 'appScopeId'},
    ConditionalAccessPolicy: {'state': 'state', 'conditions': 'conditions', 'grant_controls': 'grantControls', 'session_controls': 'sessionControls'},
    Device: {'device_id': 'deviceId', 'account_enabled': 'accountEnabled', 'operating_system': 'operatingSystem',
             'operating_system_version': 'operatingSystemVersion', 'trust_type': 'trustType', 'is_managed': 'isManaged', 'is_compliant': 'isCompliant'},
}


class SyncOrchestrator:
    def __init__(self, tenant_id=None, db=None, cancellation_flag=None, *, client=None, sync_id=None):
        self.tenant_id = tenant_id or settings.tenant_id
        self.db = db or DatabaseOperations()
        self.cancellation_flag = cancellation_flag or asyncio.Event()
        self.client = client
        self.sync_id = sync_id

    def check_cancelled(self):
        if self.cancellation_flag.is_set():
            raise asyncio.CancelledError()

    async def _read(self, path, params=None):
        self.check_cancelled()
        response = await self.client.make_request(path, params=params)
        self.check_cancelled()
        if response.get('status') != 'success' or not response.get('complete', False):
            raise RuntimeError(response.get('error') or 'Directory retrieval was incomplete')
        rows = response.get('data')
        if not isinstance(rows, list) or any(not isinstance(row, dict) or not row.get('id') for row in rows):
            raise RuntimeError('Expected a collection of identified directory objects')
        return rows

    async def _snapshot(self, model, fetch, notes=''):
        resource, attempted = model.__tablename__, now()
        try:
            rows = await fetch()
            self.check_cancelled()
            records = []
            for row in rows:
                if model is GroupMembership:
                    records.append(model(**row))
                    continue
                attributes = {name: row.get(source) for name, source in FIELDS[model].items()}
                if model is User:
                    selected = {}
                    for name in settings.entra_user_custom_attributes_list:
                        current = row
                        for part in name.split('.'):
                            current = current.get(part) if isinstance(current, dict) else None
                        selected[name] = current
                    attributes['custom_attributes'] = selected
                records.append(model(id=row['id'], tenant_id=self.tenant_id,
                    display_name=row.get('displayName', row.get('userDisplayName')), raw_json=row,
                    last_synced_at=attempted, **attributes))
            async with self.db.get_session() as session:
                # The delete and replacement commit together, after complete retrieval.
                await session.execute(delete(model).where(model.tenant_id == self.tenant_id))
                session.add_all(records)
                await session.merge(DirectorySnapshot(tenant_id=self.tenant_id, resource=resource, status='completed',
                    last_attempt_at=attempted, last_successful_at=attempted, record_count=len(records), notes=notes))
            return len(records), None
        except asyncio.CancelledError:
            await self._failed_snapshot(resource, attempted, 'Sync cancelled; prior snapshot retained', notes)
            raise
        except Exception as exc:
            from src.core.models.context_policy import sanitize_text
            error = sanitize_text(str(exc))[:1000]
            await self._failed_snapshot(resource, attempted, error, notes)
            return None, f'{resource}: {error}'

    async def _failed_snapshot(self, resource, attempted, error, notes):
        async with self.db.get_session() as session:
            snapshot = await session.get(DirectorySnapshot, (self.tenant_id, resource))
            if snapshot is None:
                snapshot = DirectorySnapshot(tenant_id=self.tenant_id, resource=resource)
                session.add(snapshot)
            snapshot.status, snapshot.last_attempt_at, snapshot.error, snapshot.notes = 'failed', attempted, error, notes

    async def _memberships(self):
        groups = await self._read('/groups', {'$select': 'id'})
        rows = []
        for group in groups:
            for member in await self._read(f"/groups/{group['id']}/members"):
                rows.append({'tenant_id': self.tenant_id, 'group_id': group['id'], 'member_id': member['id'],
                    'member_type': member.get('@odata.type', '').removeprefix('#microsoft.graph.'),
                    'member_display_name': member.get('displayName'), 'limited_information': member.get('displayName') is None,
                    'last_synced_at': now()})
        # A repeated membership should not fail a successful snapshot.
        return list({(row['group_id'], row['member_id']): row for row in rows}.values())

    async def _assignments(self):
        apps = await self._read('/servicePrincipals', {'$select': 'id'})
        rows = []
        for app in apps:
            rows.extend(await self._read(f"/servicePrincipals/{app['id']}/appRoleAssignedTo"))
        return list({row['id']: row for row in rows}.values())

    async def _history(self, **values):
        async with self.db.get_session() as session:
            await self.db.update_sync_history(session, self.sync_id, self.tenant_id, values)

    async def run_sync(self):
        await self.db.init_db()
        with sync_lock():
            if self.sync_id is None:
                async with self.db.get_session() as session:
                    history = await self.db.create_sync_history(session, self.tenant_id)
                    self.sync_id = history.id
            owned_client = self.client is None
            self.client = self.client or EntraAPIClient()
            await self._history(status=SyncStatus.RUNNING, process_id=str(os.getpid()), progress_percentage=0)
            user_fields = ['id', 'displayName', *FIELDS[User].values(), *(name.split('.')[0] for name in settings.entra_user_custom_attributes_list)]
            jobs = [
                (User, lambda: self._read('/users', {'$select': ','.join(dict.fromkeys(user_fields))}), ''),
                (Group, lambda: self._read('/groups', {'$select': ','.join(['id', 'displayName', *FIELDS[Group].values()])}), ''),
                (GroupMembership, self._memberships, 'Direct memberships. The v1.0 members source omits service principals; this snapshot does not establish complete service-principal membership.'),
                (ServicePrincipal, lambda: self._read('/servicePrincipals', {'$select': ','.join(['id', 'displayName', *FIELDS[ServicePrincipal].values()])}), ''),
                (Application, lambda: self._read('/applications', {'$select': ','.join(['id', 'displayName', *FIELDS[Application].values()])}), ''),
                (AppRoleAssignment, self._assignments, 'Assignments do not establish effective access. Group-based assignments apply to direct members; nested groups do not grant this access.'),
            ]
            if settings.SYNC_MFA_REGISTRATION:
                jobs.append((MFARegistration, lambda: self._read('/reports/authenticationMethods/userRegistrationDetails'), 'Report freshness is separate from retrieval time. Missing users are unknown, not unregistered.'))
            if settings.SYNC_DIRECTORY_ROLES:
                jobs.extend([(DirectoryRole, lambda: self._read('/roleManagement/directory/roleDefinitions'), ''),
                             (RoleAssignment, lambda: self._read('/roleManagement/directory/roleAssignments'), 'Current assignments; PIM eligibility is not included.')])
            if settings.SYNC_CONDITIONAL_ACCESS:
                jobs.append((ConditionalAccessPolicy, lambda: self._read('/identity/conditionalAccess/policies'), 'Configuration only; does not evaluate sign-in access.'))
            if settings.SYNC_DEVICES:
                jobs.append((Device, lambda: self._read('/devices', {'$select': ','.join(['id', 'displayName', *FIELDS[Device].values()])}), 'Directory inventory, not Intune management data.'))
            errors, counts = [], {}
            try:
                for index, (model, fetch, notes) in enumerate(jobs):
                    self.check_cancelled()
                    count, error = await self._snapshot(model, fetch, notes)
                    if error:
                        errors.append(error)
                    else:
                        counts[model.__tablename__] = count
                    await self._history(progress_percentage=round(100 * (index + 1) / len(jobs)),
                        users_count=counts.get('users', 0), groups_count=counts.get('groups', 0),
                        apps_count=counts.get('service_principals', 0), mfa_count=counts.get('mfa_registrations', 0),
                        policies_count=counts.get('conditional_access_policies', 0), devices_count=counts.get('devices', 0))
                status = SyncStatus.COMPLETED if not errors else SyncStatus.PARTIAL if counts else SyncStatus.FAILED
                await self._history(status=status, success=not errors, end_time=now(), sync_end_time=now(),
                    error_details='; '.join(errors) or None, records_processed=sum(counts.values()))
                return {'status': status.value, 'counts': counts, 'errors': errors}
            except asyncio.CancelledError:
                await self._history(status=SyncStatus.CANCELED, success=False, end_time=now(), error_details='Sync cancelled; unpublished snapshots retained')
                raise
            finally:
                if owned_client:
                    await self.client.close_session()
