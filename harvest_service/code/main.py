from pymongo import MongoClient
from aws_harvester import create_boto3_session, harvest_buckets, harvest_roles
from apscheduler.schedulers.blocking import BlockingScheduler
from mongo_db.shared import (
    MONGODB_URI, ACCOUNTS_DB_NAME, ACCOUNTS_COLLECTION_NAME, 
    HARVEST_DB_NAME, BUCKETS_COLLECTION_NAME, ROLES_COLLECTION_NAME
)
import os

client = MongoClient(MONGODB_URI)
accounts_db = client[ACCOUNTS_DB_NAME]
harvest_db = client[HARVEST_DB_NAME]

accounts_collection = accounts_db[ACCOUNTS_COLLECTION_NAME]

###HARVEST FOR THE EXISTING ACCOUNTS
def harvest_all_accounts():
    accounts = list(accounts_collection.find({}))
    for account in accounts:
        session = create_boto3_session(account)
        buckets_data = harvest_buckets(session)
        roles_data = harvest_roles(session)

        harvest_db[BUCKETS_COLLECTION_NAME].insert_one({
            "account_id": account["_id"],
            "data": buckets_data,
        })
        harvest_db[ROLES_COLLECTION_NAME].insert_one({
            "account_id": account["_id"],
            "data": roles_data,
        })
        print(f"Harvested account {account['_id']}")

###SCHEDULE HARVEST SERVICE EVERY 4 HOURS
if __name__ == "__main__":
    scheduler = BlockingScheduler()
    scheduler.add_job(harvest_all_accounts, 'interval', hours=4)
    print("Scheduler started... harvesting every 4 hours.")
    scheduler.start()
