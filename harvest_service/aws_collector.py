import boto3
from typing import Dict, List

###COMPLETE ACCORDING TO SPECIFICATIONS
def create_boto3_session(account: Dict):
    return boto3.Session(
        aws_access_key_id=account["aws_access_key_id"],
        aws_secret_access_key=account["aws_secret_access_key"],
        region_name=account.get("region", "us-east-1"),
    )

###COMPLETE ACCORDING TO SPECIFICATIONS
def collect_s3_info(session: boto3.Session) -> List[Dict]:
    s3 = session.client("s3")
    buckets = s3.list_buckets()["Buckets"]
    return [{"Name": b["Name"], "CreationDate": b["CreationDate"].isoformat()} for b in buckets]

###COMPLETE ACCORDING TO SPECIFICATIONS
def collect_iam_roles(session: boto3.Session) -> List[Dict]:
    iam = session.client("iam")
    roles = iam.list_roles()["Roles"]
    return [{"RoleName": r["RoleName"], "Arn": r["Arn"]} for r in roles]
