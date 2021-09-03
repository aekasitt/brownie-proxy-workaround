from os import getcwd
from pytest import fixture
from brownie import accounts, Token, TokenProxy, Wei
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
def deploy_token(account: Account) -> Token:
  print(f'Account: { account } (balance={ account.balance() })')
  print('Deployment Test for Token')
  token: Token = Token.deploy({'from': account})
  print(f'Token: { token } (name={ token.name() }, symbol={ token.symbol() }, totalSupply={ token.totalSupply() })')
  return token

@fixture
def deploy_proxy(account: Account, deploy_token: Token) -> TokenProxy:
  print('Deployment Test for Proxy')
  token = deploy_token
  print(f'Token: { token }')
  proxy: TokenProxy = TokenProxy.deploy(token.address, b'', {'from': account})
  print(f'Token Proxy: { proxy }')
  return proxy

def test_wrap_proxy(deploy_proxy: TokenProxy, file_name: str = 'Token', contract_name: str = 'Token') -> Token:
  print('Wrapping Test for Proxy on Token')
  proxy: TokenProxy = deploy_proxy
  token_proxy: Token
  try:
    token_proxy = Token.at(proxy.address)
  except ContractExists:
    with open(getcwd() + f'/contracts/{file_name}.sol') as f:
      tmp_project: Project = compile_source(f.read())
      token_proxy          = ProjectContract(tmp_project, build={'abi': Token.abi, 'contractName': contract_name}, address=proxy.address)
  print(f'Token (Proxy): { token_proxy } (name={ token_proxy.name() }, symbol={ token_proxy.symbol() }, totalSupply={ token_proxy.totalSupply() })')
  return token_proxy
