// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
import './Storage.sol';

/**
 * @notice See [repo](https://github.com/tagupta/Proxy-Contract) for origincal contract code 
 * @author Tanu Gupta (tagupta)
 */
contract Dogs is Storage {
  modifier onlyOwner() {
    require(owner == msg.sender, 'Accessible to owners only');
    _;
  }
  constructor() {
    owner = msg.sender;
  }
  function getNumberOfDogs() public view returns(uint) {
    return _uintStorage['Dogs'];
  }
  function setNumberOfDogs(uint _dogs) public virtual {
    _uintStorage['Dogs'] = _dogs;
  }
}