// SPDX-License-Identifier: BUSL-1.1
pragma solidity ^0.8.0;

import "../../contracts/role/RoleStore.sol";

contract RoleStoreHarness is RoleStore {
    using EnumerableSet for EnumerableSet.AddressSet;
    using EnumerableSet for EnumerableSet.Bytes32Set;

    constructor() RoleStore() {}

    function hasAdminRole() public view returns (bool) {
        return hasRole(msg.sender, Role.ROLE_ADMIN);
    }

    function hasRole1(bytes32 roleKey, address account) external view returns (bool) {
        return roleMembers[roleKey].contains(account);
    }
}
