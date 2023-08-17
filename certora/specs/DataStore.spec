using DataStoreHarness as dataStore;

definition INT256_MAX() returns mathint = 0x8000000000000000000000000000000000000000000000000000000000000000;

methods {
    // RoleStore.sol
    function _.hasRole(address, bytes32) external => DISPATCHER(true);
}

rule sanity_satisfy(method f) {
    env e;
    calldataarg args;
    f(e, args);
    satisfy true;
}

rule cannotApplyNegativeTwin {
    env e;
    bytes32 key;
    mathint delta;

    // Pre-conditions
    require(dataStore.hasControllerRole(e));
    require(delta < 0);
    require(-delta < INT256_MAX());
    mathint keyValue = to_mathint(dataStore.getUint(e, key));

    // Test applyDeltaToUint
    dataStore.applyDeltaToUint@withrevert(e, key, assert_int256(delta), "fail");
    bool succeeded = !lastReverted;

    // Post-conditions
    assert keyValue >= -delta <=> succeeded;
    assert keyValue < -delta <=> !succeeded;
}
