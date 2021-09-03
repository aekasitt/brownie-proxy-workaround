from os import getcwd
from pytest import fixture
from brownie import accounts, Dogs, Proxy, Wei
from brownie.network.account import Account
from brownie.network.contract import ProjectContract
from brownie.project.main import compile_source, Project
from brownie.exceptions import ContractExists
from yaml import safe_load

TERM_RED: str   = '\033[1;31m'
TERM_GREEN: str = '\033[1;32m'
TERM_NFMT: str  = '\033[0;0m'

@fixture
def account() -> Account:
  file_name: str = 'wallet.test.yml'
  ### Load Mnemonic from YAML File ###
  try:
    with open(file_name) as f:
      content = safe_load(f)
      ### Read Mnemonic ###
      mnemonic = content.get('mnemonic', None)
      acct = accounts.from_mnemonic(mnemonic, count=1)
  except FileNotFoundError:
    print(f'{TERM_RED}Cannot find wallet mnemonic file defined at `{file_name}`.{TERM_NFMT}')
    return
  ### Transfer Initial Balance to Test WAllet ###
  try:
    accounts[0].transfer(acct, Wei('100 ether').to('wei'))
  except ValueError: pass
  print(f'Test Account: { acct.address } {TERM_GREEN}(balance={ acct.balance() } wei){TERM_NFMT}')
  return acct

@fixture
def deploy_dogs(account: Account) -> Dogs:
  print(f'Account: { account } (balance={ account.balance() })')
  print('Deployment Test for Token')
  dogs: Dogs = Dogs.deploy({'from': account})
  print(f'Dogs: { dogs } (count={ dogs.getNumberOfDogs() })')
  return dogs

@fixture
def deploy_proxy(account: Account, deploy_dogs: Dogs) -> Proxy:
  print('Deployment Test for Proxy')
  dogs: Dogs = deploy_dogs
  print(f'Dogs: { dogs }')
  proxy: Proxy = Proxy.deploy(dogs.address, {'from': account})
  print(f'Proxy: { proxy }')
  return proxy

@fixture
def wrap_proxy(deploy_proxy: Proxy, file_name: str = 'Dogs', contract_name: str = 'Dogs') -> Dogs:
  print('Wrapping Test for Proxy on Token')
  proxy: Proxy = deploy_proxy
  dogs_proxy: Dogs
  try:
    dogs_proxy = Dogs.at(proxy.address)
  except ContractExists:
    with open(getcwd() + f'/contracts/{file_name}.sol') as f:
      tmp_project: Project = compile_source(f.read())
      dogs_proxy           = ProjectContract(tmp_project, build={'abi': Dogs.abi, 'contractName': contract_name}, address=proxy.address)
  print(f'Dogs (Proxy): { dogs_proxy } ({ dogs_proxy.getNumberOfDogs()})')
  return dogs_proxy

def test_proxy_dogs_params(account: Account, deploy_dogs: Dogs, wrap_proxy: Dogs):
  dogs: Dogs       = deploy_dogs
  dogs_proxy: Dogs = wrap_proxy
  count: int       = 10
  dogs_proxy.setNumberOfDogs(count, {'from': account})
  assert dogs.getNumberOfDogs() == count