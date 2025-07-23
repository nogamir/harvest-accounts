from utils.models import Account, S3Bucket, IAMRole
from utils.models import S3Bucket
import boto3

###COMPLETE ACCORDING TO SPECIFICATIONS
def create_boto3_session(account: Account):
    return boto3.Session(
        aws_access_key_id=account["aws_access_key_id"],
        aws_secret_access_key=account["aws_secret_access_key"],
        region_name="us-east-1",
    )

def harvest_buckets(session):
    s3 = session.client("s3")
    buckets_data = s3.list_buckets()["Buckets"]
    buckets = []

    for bucket_data in buckets_data:
        name = bucket_data["Name"]
        creation_date = bucket_data["CreationDate"].date()

        # Get bucket region
        region_resp = s3.get_bucket_location(Bucket=name)
        region = region_resp.get("LocationConstraint")

        # Construct bucket ARN
        bucket_arn = f"arn:aws:s3:::{name}"

        bucket = S3Bucket(
            id=name,               
            type="s3",
            bucketArn=bucket_arn,
            bucketRegion=region,
            creationDate=creation_date,
            name=name,
        )
        buckets.append(bucket)

    return buckets

def harvest_roles(session):
    iam = session.client("iam")
    roles_data = iam.list_roles()["Roles"]
    roles = []

    for role_data in roles_data:
        # Basic fields
        id = role_data["Arn"]
        role_name = role_data["RoleName"]
        role_id = role_data["RoleId"]
        create_date = role_data["CreateDate"].date()
        path = role_data.get("Path", "")
        
        last_used = role_data.get("RoleLastUsed", {}).get("LastUsedDate")
        last_used = last_used.date() if last_used else None

        tags_resp = iam.list_role_tags(RoleName=role_name)
        tags = [{tag["Key"]: tag["Value"]} for tag in tags_resp.get("Tags", [])]

        inline_policies_resp = iam.list_role_policies(RoleName=role_name)
        inline_policies_names = inline_policies_resp.get("PolicyNames", [])

        role = IAMRole(
            id=id,
            type="role",
            createDate=create_date,
            path=path,
            roleId=role_id,
            roleName=role_name,
            roleLastUsed=last_used,
            tags=tags,
            inlinePoliciesNames=inline_policies_names,
        )
        roles.append(role)

    return roles
