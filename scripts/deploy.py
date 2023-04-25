from ape import accounts, project
from ape_zksync import ZKSyncAccount


def main():
    dev = next((acct for acct in accounts if isinstance(acct, ZKSyncAccount)))
    factory = project.StableFactory.deploy(dev, sender=dev, factory_deps=[project.StableFactory__VYPER_FORWARDER_CONTRACT.contract_type.deployment_bytecode.bytecode])
    
