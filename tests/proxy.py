#!/usr/bin/env python
# coding:utf-8
# Copyright (C) 2019-2021 All rights reserved.
# FILENAME:  tests/fixtures.py
# VERSION: 	 1.0
# CREATED: 	 2021-08-22 15:05
# AUTHOR: 	 Aekasitt Guruvanich <aekazitt@gmail.com>
# DESCRIPTION:
#
# HISTORY:
#*************************************************************
'''
Test Suite for Proxying Contracts
'''
from brownie import Dogs, DogsUpdated
from brownie.exceptions import VirtualMachineError
from brownie.network.account import Account
### Import Fixtures ###
from .fixtures import *

### ANSI Coloring ###
BLUE: str  = '\033[1;34m'
RED: str   = '\033[1;31m'
GREEN: str = '\033[1;32m'
NFMT: str  = '\033[0;0m'

def test_set_number_of_dogs(admin: Account, deploy_dogs: Dogs, wrap_proxy: Dogs):
  '''
  Test setting the number of dogs to show that the Storage for both contracts aren't shared, but the logic is.
  '''
  print(f'{ BLUE }Test #1 Sets number of dogs.{ NFMT }')
  dogs: Dogs       = deploy_dogs
  dogs_proxy: Dogs = wrap_proxy
  print(f'Dogs (Based): { dogs } (count={ dogs.getNumberOfDogs() })')
  print(f'Dogs (Proxy): { dogs_proxy } (count={ dogs_proxy.getNumberOfDogs()})')
  n: int = 10
  dogs_proxy.setNumberOfDogs(n, {'from': admin})
  assert dogs.getNumberOfDogs() != dogs_proxy.getNumberOfDogs() # Storage is not shared, logic is;
  print(f'Dogs (Based): { dogs } (count={ dogs.getNumberOfDogs() })')
  print(f'Dogs (Proxy): { dogs_proxy } (count={ dogs_proxy.getNumberOfDogs()})')

def test_initialize_based(admin: Account, wrap_proxy: Dogs):
  print(f'{ BLUE }Test #2 Try to initialize Proxy with Dogs logic.{ NFMT }')
  dogs: Dogs = wrap_proxy
  error_raised: bool = False
  try:
    dogs.initialize(admin, {'from': admin})
  except AttributeError:
    error_raised = True
  assert error_raised == True
  assert dogs.owner() != admin.address

def test_initialize_updated(admin: Account, wrap_proxy_updated: DogsUpdated):
  print(f'{ BLUE }Test #3 Try to initialize Proxy with DogsUpdated logic.{ NFMT }')
  dogs_updated: DogsUpdated = wrap_proxy_updated
  error_raised: bool = False
  try:
    dogs_updated.initialize(admin, {'from': admin})
  except AttributeError:
    error_raised = True
  assert error_raised == False
  assert wrap_proxy_updated.owner() == admin

def test_set_number_of_dogs_updated(admin: Account, non_admin: Account, init_wrapped_proxy_updated: DogsUpdated):
  print(f'{ BLUE }Test #4 Sets number of dogs with non-admin account{ NFMT }')
  dogs_updated: DogsUpdated = init_wrapped_proxy_updated
  ### Sets number of dogs by Non-Admin (Reverted) ###
  n: int = 10
  try:
    dogs_updated.setNumberOfDogs(n, {'from': non_admin})
  except VirtualMachineError: pass
  assert n != dogs_updated.getNumberOfDogs()
  ### Sets number of dogs by Admin (Successful) ###
  assert dogs_updated.owner() == admin.address
  dogs_updated.setNumberOfDogs(n, {'from': admin})
  assert n == dogs_updated.getNumberOfDogs()
