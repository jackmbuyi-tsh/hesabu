import uuid

PAYMENT = {
    "merchant_reference": "INV-0001",
    "provider": "mpesa",
    "phone_number": "+243812345678",
    "amount": "25.50",
    "currency": "USD",
}


def create(client, key="key-1", **overrides):
    return client.post("/payments", json={**PAYMENT, **overrides}, headers={"Idempotency-Key": key})


def test_health(client):
    assert client.get("/health").json() == {"status": "ok"}


def test_create_payment_starts_pending(client):
    response = create(client)
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "pending"
    assert data["provider_reference"].startswith("mpesa-")
    assert data["amount"] == "25.50"


def test_same_idempotency_key_returns_same_payment(client):
    first = create(client, key="same")
    second = create(client, key="same")
    assert second.status_code == 200
    assert second.json()["id"] == first.json()["id"]


def test_idempotency_key_is_required(client):
    response = client.post("/payments", json=PAYMENT)
    assert response.status_code == 422


def test_rejects_invalid_input(client):
    assert create(client, key="a", amount="0").status_code == 422
    assert create(client, key="b", currency="EUR").status_code == 422
    assert create(client, key="c", phone_number="0812345678").status_code == 422
    assert create(client, key="d", provider="unknown").status_code == 422


def test_get_payment(client):
    created = create(client).json()
    response = client.get(f"/payments/{created['id']}")
    assert response.status_code == 200
    assert response.json()["merchant_reference"] == "INV-0001"


def test_get_unknown_payment_is_404(client):
    assert client.get(f"/payments/{uuid.uuid4()}").status_code == 404
