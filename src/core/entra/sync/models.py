"""Directory tables use Graph object IDs; shared application tables are retained."""
from sqlalchemy import Column, String, Boolean, Integer, DateTime, JSON, Text
from src.core.storage.models import Base, get_utc_now


class DirectoryRecord:
    id = Column(String, primary_key=True)
    tenant_id = Column(String, nullable=False, index=True)
    display_name = Column(String, index=True)
    raw_json = Column(JSON, nullable=False)
    last_synced_at = Column(DateTime(timezone=True), default=get_utc_now, nullable=False)


class User(DirectoryRecord, Base):
    __tablename__ = 'users'
    user_principal_name = Column(String, index=True)
    mail = Column(String, index=True)
    given_name = Column(String)
    surname = Column(String)
    account_enabled = Column(Boolean)
    user_type = Column(String)
    department = Column(String, index=True)
    job_title = Column(String)
    employee_id = Column(String)
    created_date_time = Column(String)
    custom_attributes = Column(JSON, default=dict)


class Group(DirectoryRecord, Base):
    __tablename__ = 'groups'
    description = Column(Text)
    mail = Column(String)
    security_enabled = Column(Boolean)
    mail_enabled = Column(Boolean)
    group_types = Column(JSON)
    membership_rule = Column(Text)
    is_assignable_to_role = Column(Boolean)


class GroupMembership(Base):
    __tablename__ = 'group_memberships'
    tenant_id = Column(String, primary_key=True)
    group_id = Column(String, primary_key=True)
    member_id = Column(String, primary_key=True)
    member_type = Column(String)
    member_display_name = Column(String)
    limited_information = Column(Boolean, default=False)
    last_synced_at = Column(DateTime(timezone=True), default=get_utc_now)


class ServicePrincipal(DirectoryRecord, Base):
    __tablename__ = 'service_principals'
    app_id = Column(String, index=True)
    service_principal_type = Column(String)
    account_enabled = Column(Boolean)
    app_role_assignment_required = Column(Boolean)
    app_roles = Column(JSON)


class Application(DirectoryRecord, Base):
    __tablename__ = 'applications'
    app_id = Column(String, index=True)
    sign_in_audience = Column(String)
    app_roles = Column(JSON)


class AppRoleAssignment(DirectoryRecord, Base):
    __tablename__ = 'app_role_assignments'
    resource_id = Column(String, nullable=False, index=True)
    principal_id = Column(String, nullable=False, index=True)
    principal_type = Column(String)
    principal_display_name = Column(String)
    app_role_id = Column(String)
    created_date_time = Column(String)


class MFARegistration(DirectoryRecord, Base):
    __tablename__ = 'mfa_registrations'
    user_principal_name = Column(String)
    is_mfa_registered = Column(Boolean)
    is_mfa_capable = Column(Boolean)
    is_passwordless_capable = Column(Boolean)
    methods_registered = Column(JSON)
    last_updated_date_time = Column(String)


class DirectoryRole(DirectoryRecord, Base):
    __tablename__ = 'directory_roles'
    description = Column(Text)
    is_built_in = Column(Boolean)


class RoleAssignment(DirectoryRecord, Base):
    __tablename__ = 'role_assignments'
    principal_id = Column(String, index=True)
    role_definition_id = Column(String, index=True)
    directory_scope_id = Column(String)
    app_scope_id = Column(String)


class ConditionalAccessPolicy(DirectoryRecord, Base):
    __tablename__ = 'conditional_access_policies'
    state = Column(String)
    conditions = Column(JSON)
    grant_controls = Column(JSON)
    session_controls = Column(JSON)


class Device(DirectoryRecord, Base):
    __tablename__ = 'devices'
    device_id = Column(String)
    account_enabled = Column(Boolean)
    operating_system = Column(String)
    operating_system_version = Column(String)
    trust_type = Column(String)
    is_managed = Column(Boolean)
    is_compliant = Column(Boolean)


class DirectorySnapshot(Base):
    __tablename__ = 'directory_snapshots'
    tenant_id = Column(String, primary_key=True)
    resource = Column(String, primary_key=True)
    status = Column(String, nullable=False)
    last_attempt_at = Column(DateTime(timezone=True), nullable=False)
    last_successful_at = Column(DateTime(timezone=True))
    record_count = Column(Integer)
    error = Column(Text)
    notes = Column(Text)
