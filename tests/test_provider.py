import math

import ape
import pytest


@pytest.fixture
def provider(alice, project):
    yield project.AddressProvider.deploy(alice, sender=alice)


def test_constructor(alice, provider):
    assert provider.admin() == alice
    assert provider.max_id() == 0
    assert provider.get_id_info(0).description == "Main Registry"


def test_add_new_id(alice, chain, mock_foo, provider):
    receipt = provider.add_new_id(mock_foo, "Foo", sender=alice)
    assert provider.max_id() == 1

    info = provider.get_id_info(1)
    assert info.addr == mock_foo
    assert info.is_active is True
    assert info.version == 1
    # TODO: why is TIMESTAMP opcode up to 2 seconds earlier than timestamp returned
    # by eth_getBlockBy*
    assert math.isclose(info.last_modified, chain.blocks[receipt.block_number].timestamp, abs_tol=2)
    assert info.description == "Foo"

    event = next(provider.NewAddressIdentifier.from_receipt(receipt))
    assert event.event_arguments == dict(id=1, addr=mock_foo.address, description="Foo")


def test_add_new_id_reverts_invalid_caller(bob, mock_foo, provider):
    with ape.reverts():
        provider.add_new_id(mock_foo, "Foo", sender=bob)


def test_add_new_id_reverts_invalid_address(alice, bob, provider):
    with ape.reverts():
        provider.add_new_id(bob, "Foo", sender=alice)


@pytest.mark.parametrize("id", [0, 1])
def test_set_address(alice, chain, mock_foo, provider, id):
    if id != 0:
        provider.add_new_id(mock_foo, "Foo", sender=alice)

    receipt = provider.set_address(id, mock_foo, sender=alice)

    if id == 0:
        assert provider.get_registry() == mock_foo

    info = provider.get_id_info(id)
    expected_version = 1 if id == 0 else 2
    assert info.addr == mock_foo
    assert info.is_active is True
    assert info.version == expected_version
    assert math.isclose(info.last_modified, chain.blocks[receipt.block_number].timestamp, abs_tol=2)

    event = next(provider.AddressModified.from_receipt(receipt))
    assert event.event_arguments == dict(
        id=id, new_address=mock_foo.address, version=expected_version
    )
