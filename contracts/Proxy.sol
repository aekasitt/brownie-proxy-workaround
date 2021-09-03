// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
import './Storage.sol';

/**
 * @notice See [repo](https://github.com/tagupta/Proxy-Contract) for origincal contract code 
 * @author Tanu Gupta (tagupta)
 */
contract Proxy is Storage {
  address currentAddress;
  constructor(address _address) {
    currentAddress = _address;
  }
  function upgrade(address _address) public {
    currentAddress = _address;
  }
  /**
   * @dev receive
   */
  receive() payable external {}

  /**
   * @dev fallback
   */
  fallback() payable external {
    address implementation = currentAddress;
    require(currentAddress != address(0), "Contract address is zero");
    bytes memory data = msg.data;
    assembly {
      let result := delegatecall(gas(), implementation, add(data, 0x20), mload(data), 0, 0)
      let size := returndatasize()
      let ptr := mload(0x40)
      returndatacopy(ptr, 0, size)
      switch result
      case 0 {
        revert(ptr, size)
      }
      default {
        return (ptr, size)
      }
    }
  }
}