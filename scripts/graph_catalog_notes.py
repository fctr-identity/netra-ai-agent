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

# Common administrator workflows. Relationships keep the parent's routing entity,
# but override its response type and meaning instead of inheriting object notes.
RESOURCES.update({
    'delegated_grant': {
        'type': 'oAuth2PermissionGrant', 'permission': 'Directory.Read.All',
        'fields': 'id clientId resourceId consentType principalId scope',
        'description': 'Delegated OAuth consent grants: which client may act for which users and with which scopes.',
        'interpretation': 'clientId and resourceId are service principal object ids, not application/client appIds. scope is a space-separated set of delegated permission names. AllPrincipals means tenant-wide consent; Principal scopes consent to principalId. These are delegated grants, not app-only app role assignments or proof of token use.',
        'retrieval': 'Filter by clientId with eq when looking up one enterprise app. Resolve resourceId using service_principal.get. New grants can be delayed by replication. Do not request write permission to read consent.',
        'source': 'oauth2permissiongrant-list',
    },
    'named_location': {
        'type': 'namedLocation', 'permission': 'Policy.Read.All',
        'fields': 'id displayName createdDateTime modifiedDateTime isTrusted ipRanges countriesAndRegions includeUnknownCountriesAndRegions',
        'description': 'Named IP or country locations referenced by Conditional Access policies.',
        'interpretation': 'Use @odata.type to distinguish IP and country locations; their properties differ. Join location id to policy conditions.locations include/exclude lists. All and AllTrusted are special policy selectors, not location ids. A trusted location alone does not grant access.',
        'retrieval': 'Conditional Access feature availability applies; planned for P1. Retrieve location definitions only when needed to explain targeting. Do not infer a user location from a named-location definition.',
        'source': 'conditionalaccessroot-list-namedlocations',
        'availability': 'Conditional Access; Entra P1/P2 or applicable feature entitlement.',
    },
    'authentication_strength': {
        'type': 'authenticationStrengthPolicy', 'permission': 'Policy.Read.AuthenticationMethod',
        'fields': 'id displayName description policyType requirementsSatisfied allowedCombinations createdDateTime modifiedDateTime',
        'description': 'Built-in and custom authentication strengths referenced by Conditional Access grant controls.',
        'interpretation': 'Join id to grantControls.authenticationStrength.id. allowedCombinations describes acceptable method combinations, not the methods a user has registered or used. Preserve builtIn versus custom policies.',
        'retrieval': 'Policy.Read.All is a documented higher read-only alternative. Conditional Access use requires applicable feature entitlement. Compare policy configuration with registration or sign-in evidence only when that evidence is available.',
        'source': 'authenticationstrengthroot-list-policies',
        'availability': 'Authentication strengths; Conditional Access use requires applicable P1/P2 entitlement.',
    },
    'authentication_policy': {
        'type': 'authenticationMethodsPolicy', 'permission': 'Policy.Read.AuthenticationMethod',
        'fields': 'id displayName description lastModifiedDateTime policyVersion policyMigrationState authenticationMethodConfigurations registrationEnforcement',
        'description': 'Tenant authentication-method policy, method configurations, target groups and registration enforcement.',
        'interpretation': 'This singleton is policy configuration, not a per-user registration report. Inspect each method configuration type, state, includeTargets and excludeTargets. Enabled for a target does not prove a user registered or successfully used that method. Preserve method-specific nested settings.',
        'retrieval': 'Read the singleton without collection assumptions. Policy.Read.All is a documented higher read-only alternative. Method availability depends on tenant licensing and rollout. Use the registration report for population questions.',
        'source': 'authenticationmethodspolicy-get',
        'availability': 'Method-specific tenant feature and licensing requirements apply.',
    },
    'administrative_unit': {
        'type': 'administrativeUnit', 'permission': 'AdministrativeUnit.Read.All',
        'fields': 'id displayName description visibility membershipType membershipRule membershipRuleProcessingState isMemberManagementRestricted',
        'description': 'Administrative units used to scope directory administration.',
        'interpretation': 'An administrative unit groups objects for administrative scope; it is not an access-granting security group. Join directory role assignment directoryScopeId to the unit id when the scope is /administrativeUnits/{id}. Membership is a separate relationship.',
        'retrieval': 'Preserve restricted-management and dynamic-membership properties when present. Membership rules are configuration rather than proof of evaluated membership. Missing feature-specific fields remain unknown.',
        'source': 'directory-list-administrativeunits',
        'availability': 'Administrative units; scoped administration and dynamic features have separate licensing requirements.',
    },
    'organization': {
        'type': 'organization', 'permission': 'Organization.Read.All',
        'fields': 'id displayName tenantType verifiedDomains assignedPlans onPremisesSyncEnabled onPremisesLastSyncDateTime',
        'description': 'The configured tenant organization, verified domains and reported plan/sync metadata.',
        'interpretation': 'The list returns a collection containing the current tenant organization. assignedPlans is tenant plan metadata, not per-user license assignment or complete billing evidence. Preserve unknown hybrid-sync fields.',
        'retrieval': 'Use explicit $select. Never broaden the query to another tenant. Organization id is the tenant id; use it for the detail lookup.',
        'source': 'organization-list',
    },
    'domain': {
        'type': 'domain', 'permission': 'Domain.Read.All',
        'fields': 'id authenticationType isDefault isInitial isRoot isVerified supportedServices state',
        'description': 'Tenant domains and their verification, default and authentication-type settings.',
        'interpretation': 'id is the domain name, not a GUID. Managed/Federated describes domain configuration, not whether any particular sign-in succeeds. Verification does not prove current DNS health.',
        'retrieval': 'List and filter locally: Graph documents issues with domain $search, $top and $filter. This catalog permits only $select. No DNS validation or domain mutation is performed.',
        'source': 'domain-list',
    },
    'subscribed_sku': {
        'type': 'subscribedSku', 'permission': 'LicenseAssignment.Read.All',
        'fields': 'id skuId skuPartNumber capabilityStatus consumedUnits prepaidUnits servicePlans appliesTo',
        'description': 'Subscribed license SKUs and service plans, with enabled and consumed unit counts.',
        'interpretation': 'Join user assignedLicenses.skuId to skuId, not subscribedSku.id. Detail lookups use the opaque subscribedSku.id returned by the list. consumedUnits and prepaidUnits are service-reported counts, not invoice or effective-access proof. Preserve suspended/warning capacity separately.',
        'retrieval': 'List supports only $select in this catalog; detail supports no query parameters. Organization.Read.All and Directory.Read.All are documented higher read-only alternatives. Use selected user assignedLicenses, assignedPlans and licenseAssignmentStates for user-level evidence; licenseDetails is not in the app-only catalog.',
        'source': 'subscribedsku-list',
    },
})

OPERATIONS.extend([
    ('user', 'list_direct_reports', '/users/{user_id}/directReports', '$select $filter $count'),
    ('user', 'list_app_role_assignments', '/users/{user_id}/appRoleAssignments', '$select $filter $count'),
    ('user', 'list_authentication_methods', '/users/{user_id}/authentication/methods', ''),
    ('group', 'list_owners', '/groups/{group_id}/owners', '$select $filter $search $count $top'),
    ('group', 'list_parent_groups', '/groups/{group_id}/memberOf', '$select $filter $search $count $top'),
    ('group', 'list_transitive_parent_groups', '/groups/{group_id}/transitiveMemberOf', '$select $filter $search $count $top'),
    ('group', 'list_app_role_assignments', '/groups/{group_id}/appRoleAssignments', '$select $filter $top'),
    ('device', 'list_registered_owners', '/devices/{device_id}/registeredOwners', '$select'),
    ('device', 'list_registered_users', '/devices/{device_id}/registeredUsers', '$select'),
    ('application', 'list_owners', '/applications/{application_id}/owners', '$select'),
    ('service_principal', 'list_owners', '/servicePrincipals/{service_principal_id}/owners', '$select $count'),
    ('service_principal', 'list_app_role_assignments', '/servicePrincipals/{service_principal_id}/appRoleAssignments', '$select $filter $top'),
    ('delegated_grant', 'list', '/oauth2PermissionGrants', '$filter'),
    ('named_location', 'list', '/identity/conditionalAccess/namedLocations', ''),
    ('named_location', 'get', '/identity/conditionalAccess/namedLocations/{location_id}', ''),
    ('authentication_strength', 'list', '/policies/authenticationStrengthPolicies', '$filter'),
    ('authentication_strength', 'get', '/policies/authenticationStrengthPolicies/{strength_id}', ''),
    ('authentication_policy', 'get', '/policies/authenticationMethodsPolicy', ''),
    ('role_assignment', 'get', '/roleManagement/directory/roleAssignments/{assignment_id}', '$select'),
    ('administrative_unit', 'list', '/directory/administrativeUnits', '$select $filter'),
    ('administrative_unit', 'get', '/directory/administrativeUnits/{unit_id}', '$select'),
    ('administrative_unit', 'list_members', '/directory/administrativeUnits/{unit_id}/members', '$select'),
    ('organization', 'list', '/organization', '$select'),
    ('organization', 'get', '/organization/{organization_id}', '$select'),
    ('domain', 'list', '/domains', '$select'),
    ('domain', 'get', '/domains/{domain_id}', '$select'),
    ('subscribed_sku', 'list', '/subscribedSkus', '$select'),
    ('subscribed_sku', 'get', '/subscribedSkus/{sku_id}', ''),
])

LIMITED_OBJECTS = ('Preserve id and @odata.type. Permission-limited objects may contain only identity/type and null properties. '
                   'Keep these rows as unknown detail, not nonexistent objects; resolving another type may require its own read permission. ')

OVERRIDES = {
    'user.list_direct_reports': {
        'type': 'directoryObject', 'fields': 'id displayName userPrincipalName',
        'description': 'Immediate user/contact reports for a specified manager.',
        'interpretation': LIMITED_OBJECTS + 'Only immediate reports are returned, not the entire reporting tree. Match ids rather than display names.',
        'retrieval': 'Resolve the manager as a user, then read directReports. For a manager lookup without a supported direct manager operation, an explicitly bounded enumeration of users and their directReports can establish inverse relationships; a three-row discovery sample cannot establish no manager exists.',
        'source': 'user-list-directreports',
    },
    'user.list_app_role_assignments': {
        **RESOURCES['app_role_assignment'], 'permission': 'Directory.Read.All',
        'description': 'App role assignments granted to a user, including grants through groups they directly belong to.',
        'interpretation': 'Results can include assignments granted to groups where the user is a direct member. Do not label every row a direct user assignment. Preserve principalId/principalType, join resourceId to service principal id and appRoleId to the resource appRoles. Nested groups do not confer these app assignments. Assignment is not effective access.',
        'retrieval': 'Use ConsistencyLevel eventual and $count=true as documented to include all assignments for users with many direct memberships. The adapter adds these for this operation. If Directory.Read.All is not consented, an alternative is app_role_assignment.list per known resource and direct group memberships; report its actual coverage.',
        'source': 'user-list-approleassignments', 'require_count': True,
    },
    'user.list_authentication_methods': {
        'type': 'authenticationMethod', 'permission': 'UserAuthenticationMethod.Read.All', 'fields': 'id @odata.type',
        'description': 'Optional targeted inventory of methods registered to one user.',
        'interpretation': 'Use @odata.type to distinguish method kinds. Subtypes have different fields and may expose sensitive contact details; report only the fields needed. Registration does not establish MFA use, policy eligibility or sign-in success. This API does not cover every possible authentication mechanism.',
        'retrieval': 'No query parameters. Requires separately consented method-read permission. For tenant-wide registration audits use mfa_registration.list, not repeated per-user method reads. No secrets or recovery-key endpoints are provided.',
        'source': 'authentication-list-methods', 'advanced_query': False,
        'availability': 'Optional targeted method inventory; separately consent UserAuthenticationMethod.Read.All.',
    },
    'group.list_owners': {
        'type': 'directoryObject', 'permission': 'GroupMember.Read.All', 'fields': 'id displayName userPrincipalName',
        'description': 'Owners returned for a group, with Graph v1.0 owner-visibility limitations.',
        'interpretation': LIMITED_OBJECTS + 'Owners need not be members. v1.0 currently omits service-principal owners. Owners are unavailable for Exchange-created, distribution and on-premises-synchronized groups; an empty response is not universal proof that a group is ownerless.',
        'retrieval': 'Use this relationship for ownership, not members. State the documented coverage limitation in ownerless-group reports.',
        'source': 'group-list-owners',
    },
    'group.list_app_role_assignments': {
        **RESOURCES['app_role_assignment'], 'permission': 'Directory.Read.All',
        'description': 'Enterprise application app roles assigned to a group.',
        'interpretation': 'The parent group is the assignee. resourceId identifies the enterprise application; join appRoleId to that resource appRoles. Only direct user members benefit from group-based app assignments; nested groups do not confer the grant.',
        'retrieval': 'Requires group-based assignment feature entitlement (P1/P2). Directory.Read.All is the read-only permission for this relationship. Resource-side app_role_assignment.list remains an alternative for known applications.',
        'source': 'group-list-approleassignments', 'advanced_query': False,
        'availability': 'Group-based app assignments require P1/P2.',
    },
    'service_principal.list_app_role_assignments': {
        **RESOURCES['app_role_assignment'],
        'description': 'Application permissions granted to a client service principal on resource APIs.',
        'interpretation': 'The parent service principal is the client/assignee; resourceId is the target API service principal. Join appRoleId to that resource appRoles. These are app-only grants, distinct from appRoleAssignedTo (who is assigned to this app) and delegated OAuth scopes. Requested permissions on an application registration are not proof of consent.',
        'retrieval': 'Resolve client object id first. Read resource service principals to translate permission ids. Retain unresolved resource ids instead of dropping grants.',
        'source': 'serviceprincipal-list-approleassignments', 'advanced_query': False,
    },
    'administrative_unit.list_members': {
        'type': 'directoryObject', 'fields': 'id displayName',
        'description': 'Objects directly included in an administrative unit.',
        'interpretation': LIMITED_OBJECTS + 'Adding a group to a unit does not automatically make every group member a unit member. This relationship indicates administrative scope, not application access.',
        'retrieval': 'Read all pages and retain user, group and device types separately. Hidden membership can require Member.Read.Hidden.',
        'source': 'administrativeunit-list-members',
    },
}

for operation, source, meaning in [
    ('list_parent_groups', 'group-list-memberof', 'Direct parent group and administrative-unit memberships of this group.'),
    ('list_transitive_parent_groups', 'group-list-transitivememberof', 'Transitive group memberships of this group, including nested parent groups.'),
]:
    OVERRIDES[f'group.{operation}'] = {
        'type': 'directoryObject', 'permission': 'GroupMember.ReadBasic.All', 'fields': 'id displayName',
        'description': meaning,
        'interpretation': LIMITED_OBJECTS + 'These are containers the group belongs to, not its members. Transitive nesting does not confer group-based app assignments.',
        'retrieval': 'Advanced queries use eventual consistency and $count. Inspect returned object type before interpreting a scope or relationship.',
        'source': source,
    }

for operation, source, meaning in [
    ('list_registered_owners', 'device-list-registeredowners', 'Users recorded as registered owners of the device.'),
    ('list_registered_users', 'device-list-registeredusers', 'Users recorded as registered users of the device.'),
]:
    OVERRIDES[f'device.{operation}'] = {
        'type': 'directoryObject', 'fields': 'id displayName userPrincipalName', 'description': meaning,
        'interpretation': LIMITED_OBJECTS + 'The parent device_id is its directory object id, not deviceId. Registration is not proof of current usage or an Intune primary-user assignment.',
        'retrieval': 'For a user-to-device question, enumerate the relevant devices and match user ids in this relationship. A sample or failed parent read cannot establish that a user has no devices. Preserve pagination and unknown owner details.',
        'source': source,
    }

for entity, source in [('application', 'application-list-owners'), ('service_principal', 'serviceprincipal-list-owners')]:
    OVERRIDES[f'{entity}.list_owners'] = {
        'type': 'directoryObject', 'fields': 'id displayName userPrincipalName',
        'description': f'Owners of the {entity.replace("_", " ")} object.',
        'interpretation': LIMITED_OBJECTS + 'Application registration owners and enterprise application owners are distinct relationships. Ownership is not an app-role assignment.',
        'retrieval': 'Use the parent object id, not appId. Do not assume owners are identical across a matching application and service principal.',
        'source': source,
    }
OVERRIDES['service_principal.list_owners']['require_count'] = True
OVERRIDES['service_principal.list_owners']['retrieval'] += ' Graph requires advanced-query headers and count for selected owner properties; the adapter supplies them.'

# Detail provenance must point to the detail contract, not its list counterpart.
for entity, source in {
    'user': 'user-get', 'group': 'group-get', 'device': 'device-get',
    'application': 'application-get', 'service_principal': 'serviceprincipal-get',
    'directory_role': 'unifiedroledefinition-get', 'role_assignment': 'unifiedroleassignment-get',
    'conditional_access': 'conditionalaccesspolicy-get', 'sign_in': 'signin-get',
    'directory_audit': 'directoryaudit-get', 'named_location': 'namedlocation-get',
    'authentication_strength': 'authenticationstrengthpolicy-get',
    'administrative_unit': 'administrativeunit-get', 'organization': 'organization-get',
    'domain': 'domain-get', 'subscribed_sku': 'subscribedsku-get',
}.items():
    OVERRIDES.setdefault(f'{entity}.get', {})['source'] = source

RESOURCES['user']['fields'] += ' assignedLicenses assignedPlans licenseAssignmentStates'
RESOURCES['user']['interpretation'] += ' Join assignedLicenses.skuId to subscribed_sku.skuId. licenseAssignmentStates can distinguish direct versus group licensing and assignment errors. Missing selected properties remain unknown; do not infer licenseDetails support.'
RESOURCES['device']['retrieval'] += ' For user associations use device.list_registered_owners or device.list_registered_users and match user object ids; user-side device relationships are not admitted in this app-only catalog.'
for entity in ('application', 'service_principal'):
    RESOURCES[entity]['fields'] += ' passwordCredentials keyCredentials'
    RESOURCES[entity]['retrieval'] = ('Use explicit selection for credential expiry metadata: keyId, displayName, startDateTime and endDateTime inside passwordCredentials/keyCredentials. '
        'A GET does not recover secretText. Selecting keyCredentials can also return public key bytes; omit those from answers and report only expiry metadata. '
        'Selecting keyCredentials has separate throttling limits; keep reads bounded. ' + RESOURCES[entity]['retrieval'].replace('Credentials and secrets are not part of this catalog projection. ', ''))

RESOURCES['conditional_access']['availability'] = 'Conditional Access; Entra P1/P2 or applicable feature entitlement.'
RESOURCES['conditional_access']['interpretation'] += ' Application targeting commonly uses application appId values, not service principal object ids. Resolve named-location ids through named_location reads and grantControls.authenticationStrength.id through authentication_strength.get. Preserve special selectors and exclusions.'
RESOURCES['mfa_registration']['availability'] = 'Authentication methods reporting requires P1/P2; data is report-delayed and can omit disabled/deleted users.'
RESOURCES['sign_in']['availability'] = 'Sign-in report access requires P1/P2; retention and consent constrain evidence. Risk detail may require P2.'
RESOURCES['directory_audit']['availability'] = 'Available retained audit events; retention and permissions constrain the requested window.'

SYNC_SUPPORT = {
    'user.list': 'Snapshot: users; selected base fields and configured custom attributes only.',
    'group.list': 'Snapshot: groups; selected metadata only.',
    'group.list_members': 'Snapshot: direct group_memberships; documented v1.0 type limitations.',
    'application.list': 'Snapshot: applications; selected metadata, no credential inventory.',
    'service_principal.list': 'Snapshot: service_principals; selected metadata, no owner/credential inventory.',
    'app_role_assignment.list': 'Snapshot: app_role_assignments; resource-side assignments.',
    'mfa_registration.list': 'Optional snapshot: mfa_registrations via SYNC_MFA_REGISTRATION.',
    'directory_role.list': 'Optional snapshot: directory_roles via SYNC_DIRECTORY_ROLES.',
    'role_assignment.list': 'Optional snapshot: role_assignments via SYNC_DIRECTORY_ROLES.',
    'conditional_access.list': 'Optional snapshot: conditional_access_policies via SYNC_CONDITIONAL_ACCESS.',
    'device.list': 'Optional snapshot: devices via SYNC_DEVICES; no user associations.',
}
