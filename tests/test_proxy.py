import ape
import pytest


@pytest.fixture
def proxy(alice, bob, project):
    yield project.ProxyAdmin.deploy([alice, bob], sender=alice)


def test_constructor(proxy, alice, bob):
    assert proxy.admins(0) == alice
    assert proxy.admins(1) == bob


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
