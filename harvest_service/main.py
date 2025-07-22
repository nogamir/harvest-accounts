from pymongo import MongoClient
from aws_collector import create_boto3_session, collect_s3_info, collect_iam_roles
from apscheduler.schedulers.blocking import BlockingScheduler
import os

###GET DB TABLES
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")

client = MongoClient(MONGO_URI)
accounts_db = client["accountsDB"]       # Existing DB
harvest_db = client["harvestData"]       # New DB to store collected data

accounts_collection = accounts_db["accounts"]

###HARVEST FOR THE RELEVANT ACCOUNTS
def harvest_all_accounts():
    accounts = list(accounts_collection.find({"onboarded": True}))
    for account in accounts:
        session = create_boto3_session(account)
        s3_data = collect_s3_info(session)
        iam_data = collect_iam_roles(session)

        harvest_db["s3_buckets"].insert_one({
            "account_id": account["_id"],
            "data": s3_data,
        })
        harvest_db["iam_roles"].insert_one({
            "account_id": account["_id"],
            "data": iam_data,
        })
        print(f"Harvested account {account['_id']}")

###SCHEDULE HARVEST SERVICE EVERY 4 HOURS
if __name__ == "__main__":
    scheduler = BlockingScheduler()
    scheduler.add_job(harvest_all_accounts, 'interval', hours=4)
    print("Scheduler started... harvesting every 4 hours.")
    scheduler.start()
