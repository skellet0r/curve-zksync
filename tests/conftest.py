import pathlib

import pytest
import requests
from ape_zksync.account import TestAccount, TestAccountContainer

BASE_DIR = pathlib.Path(__file__).parent.parent.absolute()


def pytest_sessionstart(session):
    try:
        response = requests.post(
            "http://localhost:3050",
            json={"jsonrpc": "2.0", "method": "web3_clientVersion", "params": [], "id": 0},
        )
        assert response.json()["result"] == "zkSync/v2.0"
    except Exception:
        raise RuntimeError(
            "zkSync v2 dev network was not found locally at 'http://localhost:3050'"
        ) from None


@pytest.fixture(scope="session")
def accounts():
    container = TestAccountContainer(data_folder=BASE_DIR, account_type=TestAccount)
    yield list(container.accounts)


@pytest.fixture(scope="session")
def alice(accounts):
    yield accounts[0]


@pytest.fixture(scope="session")
def bob(accounts):
    yield accounts[1]


@pytest.fixture(scope="session")
def charlie(accounts):
    yield accounts[2]
