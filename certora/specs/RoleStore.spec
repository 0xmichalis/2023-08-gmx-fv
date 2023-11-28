using RoleStoreHarness as roleStore;

//-----------------------------------------------------------------------------
// EnumerableSet Invariant Lib (Begin)
//-----------------------------------------------------------------------------
// Based on spec for EnumerableSet found here: https://github.com/Certora/Examples/tree/master/CVLByExample/QuantifierExamples/EnumerableSet

// GHOST COPIES
ghost mapping(bytes32 => mapping(mathint => bytes32)) ghostValues;
ghost mapping(bytes32 => mapping(bytes32 => uint256)) ghostIndexes;
ghost mapping(bytes32 => uint256) ghostLength {
    // assumption: it's infeasible to grow the list to these many elements.
    axiom forall bytes32 role. ghostLength[role] < 0xffffffffffffffffffffffffffffffff;
}

// HOOKS

hook Sstore currentContract.roleMembers[KEY bytes32 role].(offset 0) uint256 newLength STORAGE {
    ghostLength[role] = newLength;
}
hook Sstore currentContract.roleMembers[KEY bytes32 role]._inner._values[INDEX uint256 index] bytes32 newValue STORAGE {
    ghostValues[role][index] = newValue;
}
hook Sstore currentContract.roleMembers[KEY bytes32 role]._inner._indexes[KEY bytes32 value] uint256 newIndex STORAGE {
    ghostIndexes[role][value] = newIndex;
}

hook Sload uint256 length currentContract.roleMembers[KEY bytes32 role].(offset 0) STORAGE {
    require ghostLength[role] == length;
}
hook Sload bytes32 value currentContract.roleMembers[KEY bytes32 role]._inner._values[INDEX uint256 index] STORAGE {
    require ghostValues[role][index] == value;
}
hook Sload uint256 index currentContract.roleMembers[KEY bytes32 role]._inner._indexes[KEY bytes32 value] STORAGE {
    require ghostIndexes[role][value] == index;
}

// INVARIANTS

invariant hasAdminRoleInvariant(env e)
    roleStore.getAdminCount(e) > 0;

invariant setInvariant(bytes32 role)
    (forall uint256 index. 0 <= index && index < ghostLength[role] => to_mathint(ghostIndexes[role][ghostValues[role][index]]) == index + 1)
    && (forall bytes32 value. ghostIndexes[role][value] == 0 || 
         (ghostValues[role][ghostIndexes[role][value] - 1] == value && ghostIndexes[role][value] >= 1 && ghostIndexes[role][value] <= ghostLength[role]));

//-----------------------------------------------------------------------------
// Enumerable Set Invariant Lib (End)
//-----------------------------------------------------------------------------

rule sanity_satisfy(method f) {
    env e;
    calldataarg args;
    f(e, args);
    satisfy true;
}

rule grant_role_has_no_role {
    env e;
    address account;
    bytes32 role;

    uint256 roleMembersBefore;
    uint256 roleMembersAfter;

    requireInvariant setInvariant(role);
    requireInvariant hasAdminRoleInvariant(e);

    // The caller is an admin
    require(roleStore.hasAdminRole(e));
    // The account does not have the role
    require(!roleStore.hasRole(e, account, role));
    require(!roleStore.hasRole1(e, account, role));

    roleMembersBefore = roleStore.getRoleMemberCount(e, role);

    roleStore.grantRole(e, account, role);

    roleMembersAfter = roleStore.getRoleMemberCount(e, role);
    assert(roleMembersAfter > roleMembersBefore, "role member count has not changed");
}

rule grant_role_has_role {
    env e;
    address account;
    bytes32 role;

    uint256 roleMembersBefore;
    uint256 roleMembersAfter;

    requireInvariant setInvariant(role);
    requireInvariant hasAdminRoleInvariant(e);

    // The caller is an admin
    require(roleStore.hasAdminRole(e));
    // The account has the role already
    require(roleStore.hasRole(e, account, role));
    require(roleStore.hasRole1(e, account, role));

    roleMembersBefore = roleStore.getRoleMemberCount(e, role);

    roleStore.grantRole(e, account, role);

    roleMembersAfter = roleStore.getRoleMemberCount(e, role);
    assert(roleMembersAfter == roleMembersBefore, "role member count has changed");
}

rule revoke_role {
    env e;
    address account;
    bytes32 role;

    uint256 roleMembersBefore;
    uint256 roleMembersAfter;

    requireInvariant setInvariant(role);
    requireInvariant hasAdminRoleInvariant(e);

    // The caller is an admin
    require(roleStore.hasAdminRole(e));
    // The account does not have the role
    require(!roleStore.hasRole(e, account, role));
    require(!roleStore.hasRole1(e, account, role));

    roleMembersBefore = roleStore.getRoleMemberCount(e, role);

    roleStore.grantRole(e, account, role);
    roleStore.revokeRole(e, account, role);
    assert(!roleStore.hasRole(e, account, role), "role has not been revoked");

    roleMembersAfter = roleStore.getRoleMemberCount(e, role);
    assert(roleMembersAfter == roleMembersBefore, "role member count has changed");
}

rule unauthorized_access {
    env e;
    address account;
    bytes32 role;

    requireInvariant setInvariant(role);
    requireInvariant hasAdminRoleInvariant(e);

    // The caller is not an admin
    require(!roleStore.hasAdminRole(e));

    roleStore.grantRole@withrevert(e, account, role);
    assert(lastReverted, "grantRole should have reverted");
    roleStore.revokeRole@withrevert(e, account, role);
    assert(lastReverted, "revokeRole should have reverted");
}
