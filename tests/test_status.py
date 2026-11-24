import pytest

from mmgateway.models import Payment
from mmgateway.status import InvalidTransition, PaymentStatus


@pytest.mark.parametrize(
    "final", [PaymentStatus.SUCCEEDED, PaymentStatus.FAILED, PaymentStatus.EXPIRED]
)
def test_pending_can_reach_each_final_status(final):
    payment = Payment(status=PaymentStatus.PENDING)
    payment.move_to(final)
    assert payment.status is final
    assert final.is_final


@pytest.mark.parametrize(
    "start", [PaymentStatus.SUCCEEDED, PaymentStatus.FAILED, PaymentStatus.EXPIRED]
)
@pytest.mark.parametrize("target", list(PaymentStatus))
def test_final_status_never_changes(start, target):
    payment = Payment(status=start)
    with pytest.raises(InvalidTransition):
        payment.move_to(target)
    assert payment.status is start


def test_pending_cannot_go_back_to_pending():
    with pytest.raises(InvalidTransition):
        Payment(status=PaymentStatus.PENDING).move_to(PaymentStatus.PENDING)
