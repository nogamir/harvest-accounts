##################

Project Info

Harvest Accounts is a microservice-based system that retrieves AWS metadata (such as S3 buckets and IAM roles) and manages account data, storing everything securely in MongoDB. 
It is structured into two main services:

1) accounts_service: Manages AWS account metadata and APIs, and stores the accounts data in a db called accountsDB.

2) harvest_service: For each AWS account stored in the accountsDB, the service connects to this AWS account and collects S3 and IAM data. Then, it stores the data in a db called harvestDB.

##################

Setup

#######

1. Clone the repository

bash
git clone https://github.com/your-username/harvest-accounts.git
cd harvest-accounts

#######

2. Set up env file

####

a) Copy the example `.env` file:

bash
cp .env.example .env

####

b) Generate a Fernet Key for encryption/decryption of sensitive fields:

bash
python -c 
from cryptography.fernet import Fernet; 
print(Fernet.generate_key().decode())

####

c) Paste the key into your `.env`:


FERNET_KEY=your-generated-key

#######

3. Run the App with Docker Compose

####

a) Build and start all services and the MongoDB instance:

docker-compose up --build

####

b) To stop everything:

docker-compose down

##################

Testing

Run all tests using `pytest`. 

##################

Limitations

- No Exception Handling: The current implementation does not include structured exception handling. Errors from AWS clients, database operations, or internal logic may cause the application to crash or behave unpredictably.
- No Duplicate Handling: There is no logic in place to prevent or handle duplicate entries in the database (e.g., inserting the same account multiple times).
- In each service container, the utils are mapped to be inside each service folder, and not outside in a different folder, as it is in the project structure. Thus, in order to preserve the project structure for tests, they must run from within the container. Ideally, the utils would be published as a python package, and then the project structure would have been the same in all cases. 



