#!/usr/bin/env python
# coding:utf-8
# Copyright (C) 2019-2021 All rights reserved.
# FILENAME:  tests/proxy.py
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
from pytest import fixture
from brownie import accounts, Dogs, DogsUpdated, Proxy
from brownie.network.account import Account
from brownie.network.contract import ProjectContract, ContractContainer
from brownie.project.main import get_loaded_projects, Project
from brownie.exceptions import ContractExists, VirtualMachineError

### ANSI Coloring ###
BLUE: str  = '\033[1;34m'
RED: str   = '\033[1;31m'
GREEN: str = '\033[1;32m'
NFMT: str  = '\033[0;0m'

@fixture
def admin() -> Account:
  acct = accounts[0]
  return acct

@fixture
def deploy_dogs(admin: Account) -> Dogs:
  print(f'Admin Account: { admin } { GREEN }(balance={ admin.balance() }){ NFMT }')
  print(f'{ BLUE }Deployment Test for Token{ NFMT }')
  dogs: Dogs = Dogs.deploy({'from': admin})
  print(f'Dogs: { dogs } (count={ dogs.getNumberOfDogs() })')
  return dogs

@fixture
def deploy_proxy(admin: Account, deploy_dogs: Dogs) -> Proxy:
  print(f'{ BLUE }Deployment Test for Proxy{ NFMT }')
  dogs: Dogs = deploy_dogs
  print(f'Dogs: { dogs } (count={ dogs.getNumberOfDogs() })')
  proxy: Proxy = Proxy.deploy(dogs, {'from': admin})
  print(f'Proxy: { proxy }')
  return proxy

@fixture
def wrap_proxy(deploy_proxy: Proxy, contract_container: ContractContainer = Dogs, contract_name: str = 'Dogs') -> Dogs:
  print(f'{ BLUE }Wrapping Test for Proxy on Token{ NFMT }')
  proxy: Proxy = deploy_proxy
  dogs_proxy: Dogs
  try:
    dogs_proxy = Dogs.at(proxy.address)
  except ContractExists:
    project: Project = get_loaded_projects()[0]
    dogs_proxy       = ProjectContract(project, build={'abi': contract_container.abi, 'contractName': contract_name}, address=proxy.address)
  print(f'Dogs (Proxy): { dogs_proxy } (count={ dogs_proxy.getNumberOfDogs()})')
  return dogs_proxy

def test_1_set_number_of_dogs(admin: Account, deploy_dogs: Dogs, wrap_proxy: Dogs):
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

def test_2_initialize_based(admin: Account, wrap_proxy: Dogs):
  print(f'{ BLUE }Test #2 Try to initialize Proxy with Dogs logic.{ NFMT }')
  dogs: Dogs = wrap_proxy
  error_raised: bool = False
  try:
    dogs.initialize(admin, {'from': admin})
  except AttributeError:
    error_raised = True
  assert error_raised == True
  assert dogs.owner() != admin.address

@fixture
def upgrade_logic(admin: Account, deploy_proxy: Proxy):
  print(f'{ BLUE }Upgrade Logic{ NFMT }')
  proxy: Proxy              = deploy_proxy
  dogs_updated: DogsUpdated = DogsUpdated.deploy({'from': admin})
  proxy.upgrade(dogs_updated, {'from': admin})
  return proxy

@fixture
def wrap_proxy_updated(upgrade_logic: Proxy, contract_container: ContractContainer = DogsUpdated, contract_name: str = 'DogsUpdated') -> DogsUpdated:
  print(f'{ BLUE }Wrapping Proxy on DogsUpdated{ NFMT }')
  proxy: Proxy = upgrade_logic
  dogs_updated_proxy: DogsUpdated
  try:
    dogs_updated_proxy = DogsUpdated.at(proxy.address)
  except ContractExists:
    project: Project   = get_loaded_projects()[0]
    dogs_updated_proxy = ProjectContract(project, build={'abi': contract_container.abi, 'contractName': contract_name}, address=proxy.address)
  print(f'Dogs Updated (Proxy): { dogs_updated_proxy } (count={ dogs_updated_proxy.getNumberOfDogs()})')
  return dogs_updated_proxy

def test_3_initialize_updated(admin: Account, wrap_proxy_updated: DogsUpdated):
  print(f'{ BLUE }Test #3 Try to initialize Proxy with DogsUpdated logic.{ NFMT }')
  dogs_updated: DogsUpdated = wrap_proxy_updated
  error_raised: bool = False
  try:
    dogs_updated.initialize(admin, {'from': admin})
  except AttributeError:
    error_raised = True
  assert error_raised == False
  assert wrap_proxy_updated.owner() == admin
  return wrap_proxy_updated

@fixture
def init_wrapped_proxy_updated(admin: Account, wrap_proxy_updated: DogsUpdated):
  print(f'{ BLUE }Inititalze Wrapped DogsUpdated Proxy.{ NFMT }')
  dogs_updated: DogsUpdated = wrap_proxy_updated
  dogs_updated.initialize(admin, {'from': admin})
  return dogs_updated

@fixture
def non_admin() -> Account:
  acct = accounts[1]
  return acct

def test_4_set_number_of_dogs_updated(admin: Account, non_admin: Account, init_wrapped_proxy_updated: DogsUpdated):
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
