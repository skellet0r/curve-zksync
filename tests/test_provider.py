import pytest


@pytest.fixture
def provider(alice, project):
    yield project.AddressProvider.deploy(alice, sender=alice)


def test_constructor(alice, provider):
    assert provider.admin() == alice
    assert provider.max_id() == 0
    assert provider.get_id_info(0).description == "Main Registry"


def test_add_new_id(alice, chain, provider):
    receipt = provider.add_new_id(provider, "Foo", sender=alice)
    assert provider.max_id() == 1

    info = provider.get_id_info(1)
    assert info.addr == provider
    assert info.is_active is True
    assert info.version == 1
    # TODO: TIMESTAMP opcode is 2 seconds earlier than timestamp returned by eth_getBlockBy*
    # assert info.last_modified == chain.blocks[receipt.block_number].timestamp
    assert info.description == "Foo"

    event = next(provider.NewAddressIdentifier.from_receipt(receipt))
    assert event.event_arguments == dict(id=1, addr=provider.address, description="Foo")
