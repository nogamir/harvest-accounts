import pytest
import os
os.environ["FERNET_KEY"] = "QM3CAYtgFqmIe1YGQV0OncGM3ArqTa11vzGpCv2xHdk="
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch, MagicMock
from app.main import app
from app.crypto_helper import encrypt_secret, decrypt_secret


client = TestClient(app)

sample_account = {
    "id": "123",
    "name": "Test Account",
    "accessKey": "accesskey123",
    "secret": "somesecret",
}


@pytest.fixture
def mock_accounts_collection():
    mock_collection = MagicMock()
    mock_collection.insert_one = AsyncMock()
    mock_collection.update_one = AsyncMock()
    mock_collection.delete_one = AsyncMock()
    
    async def async_gen():
        yield {
            "id": "123",
            "name": "Test Account",
            "accessKey": "accesskey123",
            "secret": "encrypted-somesecret",  # Use mocked encrypted secret here
        }
    mock_collection.find = MagicMock(return_value=async_gen())
    return mock_collection

@pytest.fixture(autouse=True)
def override_accounts_collection(mock_accounts_collection):
    app.state.accounts_collection = mock_accounts_collection

@patch("app.endpoints.encrypt_secret", side_effect=lambda s: f"encrypted-{s}")
def test_add_account(mock_encrypt):
    response = client.post("/accounts", json=sample_account)
    assert response.status_code == 200
    assert response.json() == {"message": "Account added"}
    app.state.accounts_collection.insert_one.assert_awaited_once_with({
        "id": sample_account["id"],
        "name": sample_account["name"],
        "accessKey": sample_account["accessKey"],
        "secret": "encrypted-somesecret",
    })

@patch("app.endpoints.encrypt_secret", side_effect=lambda s: f"encrypted-{s}")
def test_edit_account(mock_encrypt):
    response = client.put(f"/accounts/{sample_account['id']}", json=sample_account)
    assert response.status_code == 200
    assert response.json() == {"message": "Account updated"}
    app.state.accounts_collection.update_one.assert_awaited_once_with(
        {"id": sample_account["id"]},
        {"$set": {
            "name": sample_account["name"],
            "accessKey": sample_account["accessKey"],
            "secret": "encrypted-somesecret",
        }},
    )

def test_delete_account():
    response = client.delete(f"/accounts/{sample_account['id']}")
    assert response.status_code == 200
    assert response.json() == {"message": "Account deleted"}
    app.state.accounts_collection.delete_one.assert_awaited_once_with({"id": sample_account["id"]})

@patch("app.endpoints.decrypt_secret", side_effect=lambda s: s.replace("encrypted-", ""))
def test_list_accounts(mock_decrypt):
    response = client.get("/accounts")
    assert response.status_code == 200
    data = response.json()
    assert "accounts" in data
    assert len(data["accounts"]) == 1
    account = data["accounts"][0]
    assert account["id"] == "123"
    assert account["name"] == "Test Account"
    assert account["accessKey"] == "accesskey123"
    assert account["secret"] == "somesecret"
