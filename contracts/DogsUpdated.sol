// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
import './Dogs.sol';

/**
 * @notice See [repo](https://github.com/tagupta/Proxy-Contract) for origincal contract code 
 * @author Tanu Gupta (github/tagupta)
 */
contract DogsUpdated is Dogs {
  constructor() {
    initialize(msg.sender);
  }
  function initialize(address _owner) public {
    require(_initialized == false, 'State already initialized');
    owner = _owner;
    _initialized = true;
  }
  function setNumberOfDogs(uint _dogs) public override onlyOwner {
    _uintStorage["Dogs"] = _dogs;
  }
}