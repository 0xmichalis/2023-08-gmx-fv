using DataStoreHarness as dataStore;

definition INT256_MAX() returns mathint = 0x8000000000000000000000000000000000000000000000000000000000000000;
definition UINT256_MAX() returns mathint = 0xffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff;

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
    mathint keyValue = dataStore.getUint(e, key);
    require((delta >= 0 && delta < INT256_MAX()) || (delta < 0 && -delta < INT256_MAX()));
    require(keyValue + delta < UINT256_MAX());

    // Test applyDeltaToUint
    dataStore.applyDeltaToUint@withrevert(e, key, assert_int256(delta), "fail");
    bool succeeded = !lastReverted;

    // Post-conditions
    assert succeeded <=> keyValue >= -delta, "absolute value of delta must be less than existing value in case delta is negative";
    assert !succeeded <=> keyValue < -delta, "expected revert if delta is negative and absolute value of delta is greater than existing value";
}

rule setUint {
    env e;
    bytes32 key;
    uint256 value;

    // Pre-conditions
    require(dataStore.hasControllerRole(e));

    // Test setUint
    dataStore.setUint(e, key, value);
    uint256 valueAfter = dataStore.getUint(e, key);

    // Post-conditions
    assert valueAfter == value, "uint is not set correctly";
}

rule removeUint {
    env e;
    bytes32 key;
    uint256 value;

    // Pre-conditions
    require(dataStore.hasControllerRole(e));

    // Test removeUint
    dataStore.removeUint(e, key);
    uint256 valueAfter = dataStore.getUint(e, key);

    // Post-conditions
    assert valueAfter == 0, "uint is not removed correctly";
}

rule applyDeltaToUint {
    env e;
    bytes32 key;
    uint256 delta;

    // Pre-conditions
    require(dataStore.hasControllerRole(e));
    mathint keyValue = dataStore.getUint(e, key);

    // Test applyDeltaToUint
    mathint valueAfter = dataStore.applyDeltaToUint(e, key, delta);
    mathint valueAfterStored = dataStore.getUint(e, key);

    // Post-conditions
    assert valueAfter == keyValue + to_mathint(delta), "uint is not updated correctly";
    assert valueAfter == valueAfterStored, "return argument is not the same as stored value";
}

rule applyBoundedDeltaToUint {
    env e;
    bytes32 key;
    mathint delta;

    // Pre-conditions
    require(dataStore.hasControllerRole(e));
    mathint keyValue = dataStore.getUint(e, key);
    require(keyValue + delta < UINT256_MAX());
    require((delta >= 0 && delta < INT256_MAX()) || (delta < 0 && -delta < INT256_MAX()));

    // Test applyBoundedDeltaToUint
    mathint valueAfter = dataStore.applyBoundedDeltaToUint(e, key, assert_int256(delta));
    mathint valueAfterStored = dataStore.getUint(e, key);

    // Post-conditions
    bool wouldBeNegative = delta < 0 && -delta > keyValue;
    bool shouldBeZero = delta <= 0 && -delta == keyValue;
    assert !wouldBeNegative <=> valueAfter == keyValue + delta, "uint is not updated correctly";
    assert wouldBeNegative || shouldBeZero <=> valueAfter == 0, "uint is not zero when expected";
    assert valueAfter == valueAfterStored, "return argument is not the same as stored value";
}

rule incrementUint {
    env e;
    bytes32 key;
    uint256 value;

    // Pre-conditions
    require(dataStore.hasControllerRole(e));
    mathint valueBefore = dataStore.getUint(e, key);

    // Test incrementUint
    mathint valueAfter = dataStore.incrementUint(e, key, value);
    mathint valueAfterStored = dataStore.getUint(e, key);

    // Post-conditions
    assert valueAfter == valueBefore + to_mathint(value), "uint is not incremented correctly";
    assert valueAfter == valueAfterStored, "return argument is not the same as stored value";
}

rule decrementUint {
    env e;
    bytes32 key;
    uint256 value;

    // Pre-conditions
    require(dataStore.hasControllerRole(e));
    mathint valueBefore = dataStore.getUint(e, key);

    // Test decrementUint
    mathint valueAfter = dataStore.decrementUint(e, key, value);
    mathint valueAfterStored = dataStore.getUint(e, key);

    // Post-conditions
    assert valueAfter == valueBefore - to_mathint(value), "uint is not decremented correctly";
    assert valueAfter == valueAfterStored, "return argument is not the same as stored value";
}

rule setInt {
    env e;
    bytes32 key;
    int256 value;

    // Pre-conditions
    require(dataStore.hasControllerRole(e));

    // Test setInt
    mathint valueAfter = dataStore.setInt(e, key, value);
    mathint valueAfterStored = dataStore.getInt(e, key);

    // Post-conditions
    assert valueAfter == to_mathint(value), "int is not set correctly";
    assert valueAfter == valueAfterStored, "return argument is not the same as stored value";
}

rule removeInt {
    env e;
    bytes32 key;
    int256 value;

    // Pre-conditions
    require(dataStore.hasControllerRole(e));

    // Test removeInt
    dataStore.removeInt(e, key);
    mathint valueAfter = dataStore.getInt(e, key);

    // Post-conditions
    assert valueAfter == 0, "int is not removed correctly";
}

rule applyDeltaToInt {
    env e;
    bytes32 key;
    int256 delta;

    // Pre-conditions
    require(dataStore.hasControllerRole(e));
    mathint valueBefore = dataStore.getInt(e, key);

    // Test applyDeltaToInt
    mathint valueAfter = dataStore.applyDeltaToInt(e, key, delta);
    mathint valueAfterStored = dataStore.getInt(e, key);

    // Post-conditions
    assert valueAfter == valueBefore + to_mathint(delta), "delta is not applied correctly";
    assert valueAfter == valueAfterStored, "return argument is not the same as stored value";
}

rule incrementInt {
    env e;
    bytes32 key;
    int256 value;

    // Pre-conditions
    require(dataStore.hasControllerRole(e));
    mathint valueBefore = dataStore.getInt(e, key);

    // Test incrementInt
    mathint valueAfter = dataStore.incrementInt(e, key, value);
    mathint valueAfterStored = dataStore.getInt(e, key);

    // Post-conditions
    assert valueAfter == valueBefore + to_mathint(value), "int is not incremented correctly";
    assert valueAfter == valueAfterStored, "return argument is not the same as stored value";
}

rule decrementInt {
    env e;
    bytes32 key;
    int256 delta;

    // Pre-conditions
    require(dataStore.hasControllerRole(e));
    mathint valueBefore = dataStore.getInt(e, key);

    // Test decrementInt
    mathint valueAfter = dataStore.decrementInt(e, key, delta);
    mathint valueAfterStored = dataStore.getInt(e, key);

    // Post-conditions
    assert valueAfter == valueBefore - to_mathint(delta), "int is not decremented correctly";
    assert valueAfter == valueAfterStored, "return argument is not the same as stored value";
}

rule checkUnauthorizedAccessForApplies {
    env e;
    bytes32 key;
    uint256 uintValue;
    int256 intValue;
    address addrValue;
    bool boolValue;
    bytes32 bytes32Value;
    bytes32[] bytes32ArrayValue;
    address[] addrArrayValue;
    uint256[] uintArrayValue;
    int256[] intArrayValue;
    bool[] boolArrayValue;

    // Pre-conditions
    require(!dataStore.hasControllerRole(e));

    dataStore.applyDeltaToUint@withrevert(e, key, intValue, "fail");
    assert lastReverted, "expected applyDeltaToUint with error message revert if caller does not have controller role";

    dataStore.applyDeltaToUint@withrevert(e, key, uintValue);
    assert lastReverted, "expected applyDeltaToUint revert if caller does not have controller role";

    dataStore.applyBoundedDeltaToUint@withrevert(e, key, intValue);
    assert lastReverted, "expected applyBoundedDeltaToUint revert if caller does not have controller role";

    dataStore.incrementUint@withrevert(e, key, uintValue);
    assert lastReverted, "expected incrementUint revert if caller does not have controller role";

    dataStore.decrementUint@withrevert(e, key, uintValue);
    assert lastReverted, "expected decrementUint revert if caller does not have controller role";

    dataStore.applyDeltaToInt@withrevert(e, key, intValue);
    assert lastReverted, "expected applyDeltaToInt revert if caller does not have controller role";

    dataStore.incrementInt@withrevert(e, key, intValue);
    assert lastReverted, "expected incrementInt revert if caller does not have controller role";

    dataStore.decrementInt@withrevert(e, key, intValue);
    assert lastReverted, "expected decrementInt revert if caller does not have controller role";

    dataStore.addBytes32@withrevert(e, key, bytes32Value);
    assert lastReverted, "expected addBytes32 revert if caller does not have controller role";

    dataStore.addAddress@withrevert(e, key, addrValue);
    assert lastReverted, "expected addAddress revert if caller does not have controller role";

    dataStore.addUint@withrevert(e, key, uintValue);
    assert lastReverted, "expected addUint revert if caller does not have controller role";
}

rule checkUnauthorizedAccessForSets {
    env e;
    bytes32 key;
    uint256 uintValue;
    int256 intValue;
    address addrValue;
    bool boolValue;
    bytes32 bytes32Value;
    bytes32[] bytes32ArrayValue;
    address[] addrArrayValue;
    uint256[] uintArrayValue;
    int256[] intArrayValue;
    bool[] boolArrayValue;

    // Pre-conditions
    require(!dataStore.hasControllerRole(e));

    dataStore.setUint@withrevert(e, key, uintValue);
    assert lastReverted, "expected setUint revert if caller does not have controller role";

    dataStore.setInt@withrevert(e, key, intValue);
    assert lastReverted, "expected setInt revert if caller does not have controller role";

    dataStore.setAddress@withrevert(e, key, addrValue);
    assert lastReverted, "expected setAddress revert if caller does not have controller role";

    dataStore.setBool@withrevert(e, key, boolValue);
    assert lastReverted, "expected setBool revert if caller does not have controller role";

    dataStore.setString@withrevert(e, key, "");
    assert lastReverted, "expected setString revert if caller does not have controller role";

    dataStore.setBytes32@withrevert(e, key, bytes32Value);
    assert lastReverted, "expected setBytes32 revert if caller does not have controller role";

    dataStore.setUintArray@withrevert(e, key, uintArrayValue);
    assert lastReverted, "expected setUintArray revert if caller does not have controller role";

    dataStore.setIntArray@withrevert(e, key, intArrayValue);
    assert lastReverted, "expected setIntArray revert if caller does not have controller role";

    dataStore.setAddressArray@withrevert(e, key, addrArrayValue);
    assert lastReverted, "expected setAddressArray revert if caller does not have controller role";

    dataStore.setBoolArray@withrevert(e, key, boolArrayValue);
    assert lastReverted, "expected setBoolArray revert if caller does not have controller role";

    dataStore.setBytes32Array@withrevert(e, key, bytes32ArrayValue);
    assert lastReverted, "expected setBytes32Array revert if caller does not have controller role";
}

rule checkUnauthorizedAccessForRemovals {
    env e;
    bytes32 key;
    uint256 uintValue;
    int256 intValue;
    address addrValue;
    bool boolValue;
    bytes32 bytes32Value;
    bytes32[] bytes32ArrayValue;
    address[] addrArrayValue;
    uint256[] uintArrayValue;
    int256[] intArrayValue;
    bool[] boolArrayValue;

    // Pre-conditions
    require(!dataStore.hasControllerRole(e));

    dataStore.removeUint@withrevert(e, key);
    assert lastReverted, "expected removeUint revert if caller does not have controller role";

    dataStore.removeInt@withrevert(e, key);
    assert lastReverted, "expected removeInt revert if caller does not have controller role";

    dataStore.removeAddress@withrevert(e, key);
    assert lastReverted, "expected removeAddress revert if caller does not have controller role";

    dataStore.removeBool@withrevert(e, key);
    assert lastReverted, "expected removeBool revert if caller does not have controller role";

    dataStore.removeString@withrevert(e, key);
    assert lastReverted, "expected removeString revert if caller does not have controller role";

    dataStore.removeBytes32@withrevert(e, key);
    assert lastReverted, "expected removeBytes32 revert if caller does not have controller role";

    dataStore.removeUintArray@withrevert(e, key);
    assert lastReverted, "expected removeUintArray revert if caller does not have controller role";

    dataStore.removeIntArray@withrevert(e, key);
    assert lastReverted, "expected removeIntArray revert if caller does not have controller role";

    dataStore.removeAddressArray@withrevert(e, key);
    assert lastReverted, "expected removeAddressArray revert if caller does not have controller role";

    dataStore.removeBoolArray@withrevert(e, key);
    assert lastReverted, "expected removeBoolArray revert if caller does not have controller role";

    dataStore.removeStringArray@withrevert(e, key);
    assert lastReverted, "expected removeStringArray revert if caller does not have controller role";

    dataStore.removeBytes32Array@withrevert(e, key);
    assert lastReverted, "expected removeBytes32Array revert if caller does not have controller role";
}
