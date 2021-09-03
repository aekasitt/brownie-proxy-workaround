# Workaround for Proxy Contracts on `eth-brownie`

See `tests/proxy.py` on how I did my Proxy Contract wrapping using other ContractContainers

The contracts in `contracts/` directory is a simple-to-use Proxy Example by `github/tagupta`'s repo [Proxy-Contract](https://github.com/tagupta/Proxy-Contract)

## TL;DR

The following snippet works.

```py
from brownie import Proxy, Impl
from brownie.exceptions import ContractExists
from brownie.network.contract import ProjectContract, ContractContainer
from brownie.project.main import get_loaded_projects, Project

def wrap_proxy(contract_container: ContractContainer = Impl, contract_name: str = 'Impl') -> Impl:
  impl: Impl   = Impl.at('0x...')  # Deplyed Impl
  proxy: Proxy = Proxy.at('0x...') # Deployed Proxy
  impl_proxy: Impl
  try:
    impl_proxy = Impl.at(proxy.address)
  except ContractExists:
    project: Project = get_loaded_projects()[0]
    impl_proxy       = ProjectContract(project, build={'abi': contract_container.abi, 'contractName': contract_name}, address=proxy.address)
  return impl_proxy
```
