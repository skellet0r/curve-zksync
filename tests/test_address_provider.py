import pytest


@pytest.fixture
def address_provider(alice, project):
    yield project.AddressProvider.deploy(alice, sender=alice)


def test_constructor(alice, address_provider):
    assert address_provider.admin() == alice
    assert address_provider.max_id() == 0
    assert address_provider.get_id_info(0).description == "Main Registry"
