
import os

MONGODB_URI = os.environ.get("MONGODB_URI", "mongodb://mongo:27017")

# Database names
ACCOUNTS_DB_NAME = "accountsDB"
HARVEST_DB_NAME = "harvestDB"

# Collection names
ACCOUNTS_COLLECTION_NAME = "accounts"
BUCKETS_COLLECTION_NAME = "buckets"
ROLES_COLLECTION_NAME = "roles"