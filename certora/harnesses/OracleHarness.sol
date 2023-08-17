// SPDX-License-Identifier: BUSL-1.1
pragma solidity ^0.8.0;

import {Oracle, DataStore, EventEmitter, RoleStore, OracleStore} from "../../contracts/oracle/Oracle.sol";
import {OracleUtils} from "../../contracts/oracle/OracleUtils.sol";
import {Bits} from "../../contracts/utils/Bits.sol";
import {Precision} from "../../contracts/utils/Precision.sol";
import "../../contracts/oracle/IPriceFeed.sol";
import "../../contracts/data/Keys.sol";

contract OracleHarness is Oracle {

    DataStore public immutable myDataStore;
    EventEmitter public immutable myEventEmitter;
    OracleUtils.ReportInfo public myReportInfo;
    /// @dev : struct fields of SetPricesParams. See _prepareParams().
    uint256 public mySignerInfo;
    address[] public myTokens;
    uint256[] public myCompactedMinOracleBlockNumbers;
    uint256[] public myCompactedMaxOracleBlockNumbers;
    uint256[] public myCompactedOracleTimestamps;
    uint256[] public myCompactedDecimals;
    uint256[] public myCompactedMinPrices;
    uint256[] public myCompactedMinPricesIndexes;
    uint256[] public myCompactedMaxPrices;
    uint256[] public myCompactedMaxPricesIndexes;
    bytes[] public mySignatures;
    address[] public myPriceFeedTokens;

    constructor(
        RoleStore _roleStore,
        OracleStore _oracleStore,
        DataStore _dataStore,
        EventEmitter _eventEmitter
    ) Oracle(_roleStore, _oracleStore) {
        myDataStore = _dataStore;
        myEventEmitter = _eventEmitter;
    }

    function setPrices(
        DataStore,
        EventEmitter,
        OracleUtils.SetPricesParams memory
    ) public override {
        super.setPrices(myDataStore, myEventEmitter, _prepareParams());
    }

    function _prepareParams() internal view returns (OracleUtils.SetPricesParams memory params) {
        require(mySignerInfo & Bits.BITMASK_16 > 0);
        //require(myTokens.length > 0);
        params = 
        OracleUtils.SetPricesParams(
            mySignerInfo,
            myTokens,
            myCompactedMinOracleBlockNumbers,
            myCompactedMaxOracleBlockNumbers,
            myCompactedOracleTimestamps,
            myCompactedDecimals,
            myCompactedMinPrices,
            myCompactedMinPricesIndexes,
            myCompactedMaxPrices,
            myCompactedMaxPricesIndexes,
            mySignatures,
            myPriceFeedTokens
        );
    }

    function getStablePrice(DataStore, address token) public view override returns (uint256) {
        return super.getStablePrice(myDataStore, token);
    }

    function getPriceFeedMultiplier(DataStore, address token) public view override returns (uint256) {
        return super.getPriceFeedMultiplier(myDataStore, token);
    }

    function getSignerByInfo(uint256 signerInfo, uint256 i) public view returns (address) {
        uint256 signerIndex = signerInfo >> (16 + 16 * i) & Bits.BITMASK_16;
        require (signerIndex < MAX_SIGNER_INDEX);
        return oracleStore.getSigner(signerIndex);
    }

    function validateSignerHarness(
        bytes32 SALT,
        bytes memory signature,
        address expectedSigner
    ) external view {
        OracleUtils.validateSigner(SALT, myReportInfo, signature, expectedSigner);
    }

    function feedForTokenExists(address token) public view returns (bool) {
        return myDataStore.getAddress(Keys.priceFeedKey(token)) != address(0);
    }

    function getPriceFeedMultiplier(address token) external view returns (uint256) {
        return myDataStore.getUint(Keys.priceFeedMultiplierKey(token));
    }

    function getPrice(address token) external view returns (int256) {
        address priceFeedAddress = myDataStore.getAddress(Keys.priceFeedKey(token));
        IPriceFeed priceFeed = IPriceFeed(priceFeedAddress);

        (
            /* uint80 roundID */,
            int256 price,
            /* uint256 startedAt */,
            /* uint256 timestamp */,
            /* uint80 answeredInRound */
        ) = priceFeed.latestRoundData();
        return price;
    }

    function getAdjustedPrice(int256 price, uint256 precision) external pure returns(uint256) {
        return Precision.mulDiv(uint256(price), precision, Precision.FLOAT_PRECISION);
    }

    function getPriceFeedPrice(address token) external view returns (bool, uint256) {
        return _getPriceFeedPrice(myDataStore, token);
    }
}
