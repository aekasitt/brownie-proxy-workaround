#!/usr/bin/env python
# coding:utf-8
# Copyright (C) 2019-2021 All rights reserved.
# FILENAME:  tests/__int__.py
# VERSION: 	 1.0
# CREATED: 	 2021-08-22 16:17
# AUTHOR: 	 Aekasitt Guruvanich <aekazitt@gmail.com>
# DESCRIPTION:
#
# HISTORY:
#*************************************************************
'''
Fixtures
'''
from pytest import fixture
from brownie import accounts, Dogs, DogsUpdated, Proxy
from brownie.exceptions import ContractExists
from brownie.network.account import Account
from brownie.network.contract import ProjectContract, ContractContainer
from brownie.project.main import get_loaded_projects, Project

@fixture
def admin() -> Account:
  acct = accounts[0]
  return acct

@fixture
def non_admin() -> Account:
  acct = accounts[1]
  return acct

@fixture
def deploy_dogs(admin: Account) -> Dogs:
  dogs: Dogs = Dogs.deploy({'from': admin})
  return dogs

@fixture
def deploy_proxy(admin: Account, deploy_dogs: Dogs) -> Proxy:
  dogs: Dogs = deploy_dogs
  proxy: Proxy = Proxy.deploy(dogs, {'from': admin})
  return proxy

@fixture
def wrap_proxy(deploy_proxy: Proxy, contract_container: ContractContainer = Dogs, contract_name: str = 'Dogs') -> Dogs:
  proxy: Proxy = deploy_proxy
  dogs_proxy: Dogs
  try:
    dogs_proxy = Dogs.at(proxy.address)
  except ContractExists:
    project: Project = get_loaded_projects()[0]
    dogs_proxy       = ProjectContract(project, build={'abi': contract_container.abi, 'contractName': contract_name}, address=proxy.address)
  return dogs_proxy

@fixture
def upgrade_logic(admin: Account, deploy_proxy: Proxy):
  proxy: Proxy              = deploy_proxy
  dogs_updated: DogsUpdated = DogsUpdated.deploy({'from': admin})
  proxy.upgrade(dogs_updated, {'from': admin})
  return proxy

@fixture
def wrap_proxy_updated(upgrade_logic: Proxy, contract_container: ContractContainer = DogsUpdated, contract_name: str = 'DogsUpdated') -> DogsUpdated:
  proxy: Proxy = upgrade_logic
  dogs_updated_proxy: DogsUpdated
  try:
    dogs_updated_proxy = DogsUpdated.at(proxy.address)
  except ContractExists:
    project: Project   = get_loaded_projects()[0]
    dogs_updated_proxy = ProjectContract(project, build={'abi': contract_container.abi, 'contractName': contract_name}, address=proxy.address)
  return dogs_updated_proxy

@fixture
def init_wrapped_proxy_updated(admin: Account, wrap_proxy_updated: DogsUpdated):
  dogs_updated: DogsUpdated = wrap_proxy_updated
  dogs_updated.initialize(admin, {'from': admin})
  return dogs_updated
