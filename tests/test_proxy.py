import pytest


@pytest.fixture
def proxy(alice, bob, project):
    yield project.ProxyAdmin.deploy([alice, bob], sender=alice)


def test_constructor(proxy, alice, bob):
    assert proxy.admins(0) == alice
    assert proxy.admins(1) == bob
