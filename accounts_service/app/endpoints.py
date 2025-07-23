from fastapi import APIRouter, Request
from .utils.models import Account
from utils.crypto_helper import encrypt_secret, decrypt_secret

router = APIRouter()

@router.post("/accounts")
async def add_account(account: Account, request: Request):
    encrypted_secret = encrypt_secret(account.secret)
    encrypted_account = {
        "id": account.id,
        "name": account.name,
        "accessKey": account.accessKey,
        "secret": encrypted_secret,
    }
    await request.app.state.accounts_collection.insert_one(encrypted_account)
    return {"message": "Account added"}

@router.put("/accounts/{account_id}")
async def edit_account(account_id, account: Account, request: Request):
    encrypted_secret = encrypt_secret(account.secret)
    encrypted_account = {
        "name": account.name,
        "accessKey": account.accessKey,
        "secret": encrypted_secret,
    }
    await request.app.state.accounts_collection.update_one({"id": account_id}, {"$set": encrypted_account})
    return {"message": "Account updated"}

@router.delete("/accounts/{account_id}")
async def delete_account(account_id, request: Request):
    await request.app.state.accounts_collection.delete_one({"id": account_id})
    return {"message": "Account deleted"}

@router.get("/accounts")
async def list_accounts(request: Request):
    accounts = []
    accounts_collection = request.app.state.accounts_collection.find({})
    async for account in accounts_collection:
        accounts.append({
            "id": account["id"],
            "name": account["name"],
            "accessKey": account["accessKey"],
            "secret": decrypt_secret(account["secret"]),
        })
    return {"accounts": accounts}
