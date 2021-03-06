// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * @notice See [repo](https://github.com/tagupta/Proxy-Contract) for origincal contract code 
 * @author Tanu Gupta (github/tagupta)
 */
contract Storage {
  mapping(string => uint) _uintStorage;
  mapping(string => address) _addressStorage;
  mapping(string => string) _stringStorage;
  mapping(string => bool) _boolStorage;
  mapping(string => bytes4) _bytesStorage;
  address public owner;
  bool public _initialized;
}