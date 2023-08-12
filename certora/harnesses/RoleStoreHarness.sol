// SPDX-License-Identifier: BUSL-1.1
pragma solidity ^0.8.0;

import "../../contracts/role/RoleStore.sol";

contract RoleStoreHarness is RoleStore {
    function hasAdminRole() public view returns (bool) {
        return hasRole(msg.sender, Role.ROLE_ADMIN);
    }
}
