import itertools

import ape
import pytest
from ape.utils import ZERO_ADDRESS


@pytest.fixture
def proxy(alice, bob, project):
    yield project.ProxyAdmin.deploy([alice, bob], sender=alice)


def test_constructor(proxy, alice, bob):
    assert proxy.admins(0) == alice
    assert proxy.admins(1) == bob


def test_execute(proxy, alice, mock_foo):
    calldata = b"\xcd\xe4\xef\xa9"
    receipt = proxy.execute(mock_foo, calldata, sender=alice)

    assert mock_foo.switch() is True

    event = next(proxy.TransactionExecuted.from_receipt(receipt))
    assert event.event_arguments == dict(admin=alice, target=mock_foo, calldata=calldata, value=0)


def test_execute_reverts_invalid_caller(proxy, charlie, mock_foo):
    with ape.reverts():
        proxy.execute(mock_foo, b"\xcd\xe4\xef\xa9", sender=charlie)


def test_request_admin_change(proxy, alice, charlie):
    receipt = proxy.request_admin_change(charlie, sender=alice)

    assert proxy.pending_current_admin() == 1
    assert proxy.pending_new_admin() == charlie

    event = next(proxy.RequestAdminChange.from_receipt(receipt))
    assert event.event_arguments == dict(current_admin=alice, future_admin=charlie)


def test_request_admin_change_reverts_active_request(proxy, alice, bob, charlie):
    proxy.request_admin_change(charlie, sender=alice)

    with ape.reverts():
        proxy.request_admin_change(charlie, sender=bob)


def test_request_admin_change_reverts_already_admin(proxy, alice, bob):
    with ape.reverts():
        proxy.request_admin_change(bob, sender=alice)


def test_request_admin_change_reverts_caller_not_admin(proxy, charlie):
    with ape.reverts():
        proxy.request_admin_change(charlie, sender=charlie)


def test_approve_admin_change(proxy, alice, bob, charlie):
    proxy.request_admin_change(charlie, sender=alice)
    receipt = proxy.approve_admin_change(sender=bob)

    assert proxy.change_approved() is True

    event = next(proxy.ApproveAdminChange.from_receipt(receipt))
    assert event.event_arguments == dict(
        current_admin=alice, future_admin=charlie, calling_admin=bob
    )


def test_approve_admin_change_reverts_no_active_request(proxy, alice):
    with ape.reverts():
        proxy.approve_admin_change(sender=alice)


def test_approve_admin_change_reverts_invalid_caller(proxy, alice, charlie):
    proxy.request_admin_change(charlie, sender=alice)
    with ape.reverts():
        proxy.approve_admin_change(sender=alice)


@pytest.mark.parametrize("idx,should_approve", itertools.product([0, 1], [False, True]))
def test_revoke_admin_change(proxy, alice, bob, charlie, idx, should_approve):
    revoker = [alice, bob][idx]

    proxy.request_admin_change(charlie, sender=alice)
    if should_approve:
        proxy.approve_admin_change(sender=bob)

    receipt = proxy.revoke_admin_change(sender=revoker)

    assert proxy.pending_current_admin() == 0
    assert proxy.pending_new_admin() == ZERO_ADDRESS
    assert proxy.change_approved() is False

    event = next(proxy.RevokeAdminChange.from_receipt(receipt))
    assert event.event_arguments == dict(
        current_admin=alice, future_admin=charlie, calling_admin=revoker
    )


def test_revoke_admin_change_reverts_caller_is_not_admin(proxy, charlie):
    with ape.reverts():
        proxy.revoke_admin_change(sender=charlie)


def test_accept_admin_change(proxy, alice, bob, charlie):
    proxy.request_admin_change(charlie, sender=alice)
    proxy.approve_admin_change(sender=bob)

    receipt = proxy.accept_admin_change(sender=charlie)

    assert proxy.admins(0) == charlie

    assert proxy.pending_current_admin() == 0
    assert proxy.pending_new_admin() == ZERO_ADDRESS
    assert proxy.change_approved() is False

    event = next(proxy.AcceptAdminChange.from_receipt(receipt))
    assert event.event_arguments == dict(previous_admin=alice, current_admin=charlie)


def test_accept_admin_change_reverts_not_approved(proxy, alice, charlie):
    proxy.request_admin_change(charlie, sender=alice)
    with ape.reverts():
        proxy.accept_admin_change(sender=charlie)


def test_accept_admin_change_reverts_invalid_caller(proxy, alice, bob, charlie):
    proxy.request_admin_change(charlie, sender=alice)
    proxy.approve_admin_change(sender=bob)
    with ape.reverts():
        proxy.accept_admin_change(sender=alice)
