import pathlib

import pytest
from ape_zksync.account import TestAccount, TestAccountContainer

BASE_DIR = pathlib.Path(__file__).parent.parent.absolute()


@pytest.fixture(scope="session")
def accounts():
    container = TestAccountContainer(data_folder=BASE_DIR, account_type=TestAccount)
    yield list(container.accounts)


@pytest.fixture(scope="session")
def alice(accounts):
    yield accounts[0]


@pytest.fixture(scope="session")
def bob(accounts):
    yield accounts[0]


@pytest.fixture(scope="session")
def charlie(accounts):
    yield accounts[0]
