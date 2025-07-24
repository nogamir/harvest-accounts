from pymongo import MongoClient, UpdateOne, DeleteMany
from aws_harvester import create_boto3_session, harvest_buckets, harvest_roles
from apscheduler.schedulers.blocking import BlockingScheduler
from utils.db_shared import (
    MONGODB_URI, ACCOUNTS_DB_NAME, ACCOUNTS_COLLECTION_NAME, 
    HARVEST_DB_NAME, BUCKETS_COLLECTION_NAME, ROLES_COLLECTION_NAME
)
import os

client = MongoClient(MONGODB_URI)
accounts_db = client[ACCOUNTS_DB_NAME]
harvest_db = client[HARVEST_DB_NAME]

accounts_collection = accounts_db[ACCOUNTS_COLLECTION_NAME]


def harvest_all_accounts():
    # Fetch active accounts
    accounts = list(accounts_collection.find({}))
    account_ids = [acc["_id"] for acc in accounts]

    # Remove buckets and roles for inactive accounts
    harvest_db[BUCKETS_COLLECTION_NAME].delete_many({"account_id": {"$nin": account_ids}})
    harvest_db[ROLES_COLLECTION_NAME].delete_many({"account_id": {"$nin": account_ids}})

    # For each active account, harvest active buckets and roles
    for account in accounts:
        session       = create_boto3_session(account)
        buckets_data  = harvest_buckets(session)
        roles_data    = harvest_roles(session)

        # Get active buckets and roles
        bucket_ids = {b["id"] for b in buckets_data}
        role_ids   = {r["id"] for r in roles_data}

        # Remove inactive buckets and roles
        harvest_db[BUCKETS_COLLECTION_NAME].delete_many({
            "account_id": account["_id"],
            "id": {"$nin": list(bucket_ids)}
        })
        harvest_db[ROLES_COLLECTION_NAME].delete_many({
            "account_id": account["_id"],
            "id": {"$nin": list(role_ids)}
        })
        # Upsert the active buckets and roles
        bucket_ops = [
            UpdateOne(
                {"account_id": account["_id"], "id": b["id"]},
                {"$set": b, "$setOnInsert": {"account_id": account["_id"]}},
                upsert=True
            ) for b in buckets_data
        ]
        role_ops = [
            UpdateOne(
                {"account_id": account["_id"], "id": r["id"]},
                {"$set": r, "$setOnInsert": {"account_id": account["_id"]}},
                upsert=True
            ) for r in roles_data
        ]
        if bucket_ops:
            harvest_db[BUCKETS_COLLECTION_NAME].bulk_write(bucket_ops, ordered=False)
        if role_ops:
            harvest_db[ROLES_COLLECTION_NAME].bulk_write(role_ops, ordered=False)


###SCHEDULE HARVEST SERVICE EVERY 4 HOURS
if __name__ == "__main__":
    scheduler = BlockingScheduler()
    scheduler.add_job(harvest_all_accounts, 'interval', seconds=20)
    scheduler.start()
    