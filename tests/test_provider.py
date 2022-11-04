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
    # TODO: TIMESTAMP opcode is 2 seconds earlier than timestamp returned by eth_getBlockBy*
    # assert info.last_modified == chain.blocks[receipt.block_number].timestamp
    assert info.description == "Foo"

    event = next(provider.NewAddressIdentifier.from_receipt(receipt))
    assert event.event_arguments == dict(id=1, addr=mock_foo.address, description="Foo")


def test_add_new_id_reverts_invalid_caller(bob, mock_foo, provider):
    with ape.reverts():
        provider.add_new_id(mock_foo, "Foo", sender=bob)


def test_add_new_id_reverts_invalid_address(alice, bob, provider):
    with ape.reverts():
        provider.add_new_id(bob, "Foo", sender=alice)
