"""Maintainer-owned Graph guidance, merged with pinned OpenAPI metadata.

Source links belong here, never in the generated agent catalogs.
"""
REVISION = '15780e98e1082517bc7a39a6b75b356a085326d9'
REVIEWED = '2026-10-09'

RESOURCES = {
    'user': {
        'type': 'user', 'permission': 'User.Read.All',
        'fields': 'id displayName userPrincipalName mail givenName surname accountEnabled userType department jobTitle employeeId createdDateTime onPremisesExtensionAttributes',
        'description': 'Directory users, including members and guests. Use explicit selected properties for account state and organizational attributes.',
        'interpretation': 'Object id is the stable directory identifier. userPrincipalName is a sign-in name; mail can be absent and differs from UPN. accountEnabled is an account setting, not proof of successful sign-in or effective access. userType distinguishes Member and Guest. Missing properties remain unknown; never coerce missing accountEnabled to false. Membership and enterprise-app assignments require their own relationships.',
        'retrieval': 'The default user response contains only a basic property subset. Select the properties needed by the question; department and accountEnabled require selection. List does not support $skip. Default page size is 100, maximum 999; signInActivity queries have a lower 500 maximum and additional permissions. This catalog omits signInActivity; use bounded sign-in reads for event evidence. Several personal profile properties are only available on the single-user operation. Directory/schema extensions and onPremisesExtensionAttributes require $select; open extensions use a different mechanism and are outside this initial contract. Recent changes can lag in queries.',
        'source': 'user-list',
    },
    'group': {
        'type': 'group', 'permission': 'Group.Read.All',
        'fields': 'id displayName description mail securityEnabled mailEnabled groupTypes membershipRule isAssignableToRole',
        'description': 'Directory group metadata and membership relationships. Group configuration and group membership are separate reads.',
        'interpretation': 'securityEnabled, mailEnabled and groupTypes describe distinct properties. Unified identifies a Microsoft 365 group; DynamicMembership describes dynamic membership. A membership rule is configuration, not a historical evaluation result. Read actual members when the question asks who belongs. Direct memberships and transitive memberships answer different questions.',
        'retrieval': 'Use explicit field selection. Use supported filter expressions, not arbitrary substring tests on every property. Advanced directory queries use eventual consistency and can lag. Membership-only access may use GroupMember.Read.All; richer metadata requested by Netra sync uses Group.Read.All. Hidden membership additionally requires Member.Read.Hidden.',
        'source': 'group-list',
    },
    'service_principal': {
        'type': 'servicePrincipal', 'permission': 'Application.Read.All',
        'fields': 'id appId displayName servicePrincipalType accountEnabled appRoleAssignmentRequired appRoles tags preferredSingleSignOnMode',
        'description': 'Enterprise applications represented by service principals in this tenant. Use these objects for assignment reports.',
        'interpretation': 'id identifies the tenant service principal; appId identifies its application/client. These identifiers are not interchangeable. A service principal can exist without a locally owned application registration. appRoleAssignmentRequired is a configuration flag, not evidence that every assigned person can sign in. appRoles describe resource-defined roles; join assignment appRoleId to the corresponding role id.',
        'retrieval': 'Select the needed properties. Use appRoleAssignedTo for principals assigned to this resource. Do not replace that relationship with appRoleAssignments, which concerns permissions held by a client. Preserve disabled service principals unless the question excludes them.',
        'source': 'serviceprincipal-list',
    },
    'application': {
        'type': 'application', 'permission': 'Application.Read.All',
        'fields': 'id appId displayName signInAudience appRoles createdDateTime',
        'description': 'Application registrations owned in the directory. Enterprise applications and their assignments are represented by service principals.',
        'interpretation': 'Application object id, application appId, and service principal id have different uses. Join application.appId to servicePrincipal.appId when registration context is needed. A registration does not enumerate its user/group assignments. Never infer credential expiry or sign-in activity from application creation time.',
        'retrieval': 'Use only properties needed for the report. Credentials and secrets are not part of this catalog projection. Follow every collection page for registration inventory.',
        'source': 'application-list',
    },
    'app_role_assignment': {
        'type': 'appRoleAssignment', 'permission': 'Application.Read.All',
        'fields': 'id principalId principalType principalDisplayName resourceId resourceDisplayName appRoleId createdDateTime',
        'description': 'Principals assigned an app role on a specific enterprise application. Preserve User, Group and ServicePrincipal assignments separately.',
        'interpretation': 'The parent is the resource service principal. resourceId identifies that same resource; principalId identifies the assignee. A Group assignment describes a group grant, not a separate direct assignment for each member. Expand only direct users of the assigned group when answering group-based app assignment questions; nested-group membership does not confer this group-based app assignment. All-zero appRoleId is the default role, not a missing assignment. Assignment does not establish successful or effective sign-in.',
        'retrieval': 'Resolve the enterprise application first unless its service-principal id is already known. Preserve every assignment and principal type. A newly changed assignment may take time to appear. Join role definitions from that resource service principal and resolve principal names only when needed.',
        'source': 'serviceprincipal-list-approleassignedto',
    },
    'mfa_registration': {
        'type': 'userRegistrationDetails', 'permission': 'AuditLog.Read.All',
        'fields': 'id userPrincipalName userDisplayName isMfaRegistered isMfaCapable isPasswordlessCapable methodsRegistered lastUpdatedDateTime',
        'description': 'Authentication-method registration report. Use for population MFA registration questions, with report availability and freshness stated.',
        'interpretation': 'isMfaRegistered, isMfaCapable and isPasswordlessCapable answer different questions. Registration does not prove an MFA challenge was required or completed. id is the user object id. Join users to this report with a LEFT JOIN and retain missing rows as unknown. Disabled or deleted users can be absent; no report row does not mean MFA is unregistered.',
        'retrieval': 'Requires the authentication-method activity/report entitlement, planned for P1. Reports can lag; use lastUpdatedDateTime and distinguish it from Netra retrieval time. The supported query parameter in this catalog is $filter. Filter only documented report properties: isMfaRegistered, isMfaCapable, isSsprRegistered, isSsprEnabled, isSsprCapable, isPasswordlessCapable, userDisplayName, userPrincipalName, methodsRegistered. Do not add $select or $top automatically. A permission/license failure remains an unavailable report, not an empty population.',
        'source': 'authenticationmethodsroot-list-userregistrationdetails',
    },
    'directory_role': {
        'type': 'unifiedRoleDefinition', 'permission': 'RoleManagement.Read.Directory',
        'fields': 'id displayName description isBuiltIn isEnabled templateId rolePermissions',
        'description': 'Entra directory role definitions, including their named permissions. Assignments are separate records.',
        'interpretation': 'A role definition says what the role permits. It does not say who holds that role. Use role_assignment records and join roleDefinitionId to id. Built-in template ids and role definition ids have distinct uses. PIM eligibility is outside this contract.',
        'retrieval': 'Use the directory RBAC provider only. Filter supported id, displayName and isBuiltIn properties using documented equality/in comparisons. Do not substitute the activated-directoryRoles collection for all available role definitions.',
        'source': 'rbacapplication-list-roledefinitions',
    },
    'role_assignment': {
        'type': 'unifiedRoleAssignment', 'permission': 'RoleManagement.Read.Directory',
        'fields': 'id principalId roleDefinitionId directoryScopeId appScopeId',
        'description': 'Current directory role assignments with principal, role definition and scope identifiers.',
        'interpretation': 'Join principalId to the corresponding directory object and roleDefinitionId to role definitions. A slash directoryScopeId represents tenant scope; other scopes need explicit interpretation. Group assignments are distinct from direct user assignments. These reads do not enumerate PIM-eligible roles or historical activations.',
        'retrieval': 'Preserve directoryScopeId and appScopeId. Resolve missing names using approved reads rather than dropping unresolved principals. Do not claim an effective-permissions evaluation from the assignment inventory.',
        'source': 'rbacapplication-list-roleassignments',
    },
    'conditional_access': {
        'type': 'conditionalAccessPolicy', 'permission': 'Policy.Read.All',
        'fields': 'id displayName state createdDateTime modifiedDateTime conditions grantControls sessionControls',
        'description': 'Conditional Access policy configuration, including policy state, conditions and controls.',
        'interpretation': 'enabled, disabled and enabledForReportingButNotEnforced are different states. Preserve include and exclude populations, grant-control operators and session controls. Report-only policies do not enforce access. A policy inventory cannot predict a complete sign-in decision: several policies and runtime facts may apply.',
        'retrieval': 'Planned for a P1 tenant. Missing conditions or fields are not permission to invent defaults. This catalog permits full inventory/detail reads; apply unsupported comparisons locally. Never execute a policy change.',
        'source': 'conditionalaccessroot-list-policies',
    },
    'sign_in': {
        'type': 'signIn', 'permission': 'AuditLog.Read.All',
        'fields': 'id createdDateTime userId userDisplayName userPrincipalName appId appDisplayName resourceDisplayName ipAddress clientAppUsed isInteractive status conditionalAccessStatus correlationId',
        'description': 'Retained sign-in event evidence for a bounded time window. Use for observed activity, not current directory configuration.',
        'interpretation': 'status.errorCode equal to zero identifies a successful event. A successful event alone does not prove an MFA challenge occurred in that event. Absence in the retained window is not proof a user never signed in. Conditional Access details can require additional permissions and be omitted. Do not infer P2 risk fields from missing values.',
        'retrieval': 'Use an explicit createdDateTime range and preserve requested event filters. This source is live only in the initial POC. P1/P2 entitlement and retention affect available events. Follow continuation pages; report the time window and unavailable evidence. Do not fetch all tenant history without a bound.',
        'source': 'signIn-list',
    },
    'directory_audit': {
        'type': 'directoryAudit', 'permission': 'AuditLog.Read.All',
        'fields': 'id activityDateTime activityDisplayName category result resultReason initiatedBy targetResources correlationId loggedByService',
        'description': 'Retained directory audit events describing changes and administrative activity in a bounded time window.',
        'interpretation': 'Audit activity and sign-in activity are different event streams. initiatedBy identifies the actor; targetResources identifies affected objects. The result applies to that recorded activity. Preserve modified property details and event time when explaining a change; current object state does not establish who changed it.',
        'retrieval': 'Supply an explicit activityDateTime range. Use only documented filter properties and keep incomplete/expired retention evidence visible. The initial POC queries this source live and does not sync event history.',
        'source': 'directoryaudit-list',
    },
    'device': {
        'type': 'device', 'permission': 'Device.Read.All',
        'fields': 'id deviceId displayName accountEnabled operatingSystem operatingSystemVersion trustType isManaged isCompliant',
        'description': 'Entra directory device objects and reported device properties. This is not an Intune device-management inventory.',
        'interpretation': 'id is the directory object id; deviceId is the device registration identifier. accountEnabled, isManaged and isCompliant describe different states and may be missing. Do not infer compliance from accountEnabled, operating system, or trust type. Directory presence does not prove a device is currently online.',
        'retrieval': 'Preserve null and omitted flags as unknown. Device management, installed software, and live device posture require separate APIs outside this catalog.',
        'source': 'device-list',
    },
}

# entity, operation, path, allowed query parameters; SDK paths are checked in OpenAPI.
OPERATIONS = [
    ('user', 'list', '/users', '$select $filter $search $orderby $count $top'),
    ('user', 'get', '/users/{user_id}', '$select'),
    ('group', 'list', '/groups', '$select $filter $search $orderby $count $top'),
    ('group', 'get', '/groups/{group_id}', '$select'),
    ('service_principal', 'list', '/servicePrincipals', '$select $filter $search $orderby $count $top'),
    ('service_principal', 'get', '/servicePrincipals/{service_principal_id}', '$select'),
    ('application', 'list', '/applications', '$select $filter $search $orderby $count $top'),
    ('application', 'get', '/applications/{application_id}', '$select'),
    ('app_role_assignment', 'list', '/servicePrincipals/{service_principal_id}/appRoleAssignedTo', '$select $filter $top'),
    ('mfa_registration', 'list', '/reports/authenticationMethods/userRegistrationDetails', '$filter'),
    ('directory_role', 'list', '/roleManagement/directory/roleDefinitions', '$filter $select'),
    ('directory_role', 'get', '/roleManagement/directory/roleDefinitions/{role_id}', '$select'),
    ('role_assignment', 'list', '/roleManagement/directory/roleAssignments', '$filter $select'),
    ('conditional_access', 'list', '/identity/conditionalAccess/policies', ''),
    ('conditional_access', 'get', '/identity/conditionalAccess/policies/{policy_id}', ''),
    ('sign_in', 'list', '/auditLogs/signIns', '$filter $top'),
    ('sign_in', 'get', '/auditLogs/signIns/{sign_in_id}', ''),
    ('directory_audit', 'list', '/auditLogs/directoryAudits', '$filter $orderby $top'),
    ('directory_audit', 'get', '/auditLogs/directoryAudits/{audit_id}', ''),
    ('device', 'list', '/devices', '$select $filter $search $orderby $count $top'),
    ('device', 'get', '/devices/{device_id}', '$select'),
]

MEMBERSHIPS = [
    ('group', 'list_members', '/groups/{group_id}/members', 'group-list-members', False),
    ('group', 'list_transitive_members', '/groups/{group_id}/transitiveMembers', 'group-list-transitivemembers', True),
    ('user', 'list_groups', '/users/{user_id}/memberOf/microsoft.graph.group', 'user-list-memberof', False),
    ('user', 'list_transitive_groups', '/users/{user_id}/transitiveMemberOf/microsoft.graph.group', 'user-list-transitivememberof', True),
]
