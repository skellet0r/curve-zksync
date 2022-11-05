import math

import ape
import pytest
from ape.utils import ZERO_ADDRESS


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


def test_set_address_reverts_invalid_caller(bob, mock_foo, provider):
    with ape.reverts():
        provider.set_address(0, mock_foo, sender=bob)


def test_set_address_reverts_invalid_address(alice, bob, provider):
    with ape.reverts():
        provider.set_address(0, bob, sender=alice)


def test_set_address_reverts_invalid_id(alice, mock_foo, provider):
    with ape.reverts():
        provider.set_address(42, mock_foo, sender=alice)


@pytest.mark.parametrize("id", [0, 1])
def test_unset_address(alice, chain, mock_foo, provider, id):
    if id == 0:
        provider.set_address(0, mock_foo, sender=alice)
    else:
        provider.add_new_id(mock_foo, "Foo", sender=alice)

    receipt = provider.unset_address(id, sender=alice)

    if id == 0:
        assert provider.get_registry() == ZERO_ADDRESS

    info = provider.get_id_info(id)
    assert info.addr == ZERO_ADDRESS
    assert info.is_active is False
    assert info.version == 1
    assert math.isclose(info.last_modified, chain.blocks[receipt.block_number].timestamp, abs_tol=2)

    event = next(provider.AddressModified.from_receipt(receipt))
    assert event.event_arguments == dict(id=id, new_address=ZERO_ADDRESS, version=1)


def test_unset_address_reverts_invalid_caller(bob, provider):
    with ape.reverts():
        provider.unset_address(0, sender=bob)


def test_unset_address_reverts_invalid_id(alice, provider):
    with ape.reverts():
        provider.unset_address(0, sender=alice)


def test_commit_transfer_ownership(alice, bob, chain, provider):
    receipt = provider.commit_transfer_ownership(bob, sender=alice)

    deadline = provider.transfer_ownership_deadline()
    assert provider.future_admin() == bob
    assert math.isclose(
        deadline, chain.blocks[receipt.block_number].timestamp + 3 * 86400, abs_tol=2
    )

    event = next(provider.CommitNewAdmin.from_receipt(receipt))
    assert event.event_arguments == dict(deadline=deadline, admin=bob.address)


def test_commit_transfer_ownership_reverts_invalid_caller(bob, provider):
    with ape.reverts():
        provider.commit_transfer_ownership(bob, sender=bob)


def test_commit_transfer_ownership_reverts_active_transfer(alice, bob, charlie, provider):
    provider.commit_transfer_ownership(bob, sender=alice)
    with ape.reverts():
        provider.commit_transfer_ownership(charlie, sender=alice)


@pytest.mark.skip(reason="evm_(mine|setTime) RPC method unavailable")
def test_apply_transfer_ownership(alice, bob, chain, provider):
    provider.commit_transfer_ownership(bob, sender=alice)
    chain.mine(deltatime=3 * 86400)
    provider.apply_transfer_ownership(sender=alice)

    assert provider.admin() == bob
    assert provider.transfer_ownership_deadline() == 0


def test_apply_transfer_ownership_reverts_invalid_caller(bob, provider):
    with ape.reverts():
        provider.apply_transfer_ownership(sender=bob)


def test_apply_transfer_ownership_reverts_inactive_transfer(alice, provider):
    with ape.reverts():
        provider.apply_transfer_ownership(sender=alice)


def test_apply_transfer_ownership_reverts_too_early(alice, bob, provider):
    provider.commit_transfer_ownership(bob, sender=alice)
    with ape.reverts():
        provider.apply_transfer_ownership(sender=alice)


def test_revert_transfer_ownership(alice, bob, provider):
    provider.commit_transfer_ownership(bob, sender=alice)
    provider.revert_transfer_ownership(sender=alice)

    assert provider.transfer_ownership_deadline() == 0


def test_revert_transfer_ownership_reverts_invalid_caller(bob, provider):
    with ape.reverts():
        provider.revert_transfer_ownership(sender=bob)
