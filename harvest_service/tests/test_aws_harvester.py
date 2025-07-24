import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime
from utils.models import Account, S3Bucket, IAMRole
from src.aws_harvester import create_boto3_session, harvest_buckets, harvest_roles

@pytest.fixture
def mock_account():
    return Account(
        id="123",
        name="test-account",
        accessKey="fake-access",
        secret="encrypted-secret"
    )

@patch("aws_harvester.decrypt_secret", return_value="fake-secret")
def test_create_boto3_session(mock_decrypt, mock_account):
    with patch("aws_harvester.boto3.Session") as mock_session:
        session = create_boto3_session(mock_account)
        mock_session.assert_called_with(
            aws_access_key_id="fake-access",
            aws_secret_access_key="fake-secret",
            region_name="eu-north-1"
        )

def test_harvest_buckets():
    mock_s3 = MagicMock()
    mock_s3.list_buckets.return_value = {
        "Buckets": [
            {
                "Name": "test-bucket",
                "CreationDate": datetime(2020, 1, 1),
            }
        ]
    }
    mock_s3.get_bucket_location.return_value = {"LocationConstraint": None}
    session = MagicMock()
    session.client.return_value = mock_s3

    buckets = harvest_buckets(session)
    bucket = S3Bucket(**buckets[0])
    assert bucket.id == "test-bucket"
    assert bucket.name == "test-bucket"
    assert bucket.bucketRegion == "us-east-1"
    assert bucket.type == "s3"
    assert bucket.bucketArn == "arn:aws:s3:::test-bucket"
    assert bucket.creationDate == datetime(2020, 1, 1)

def test_harvest_buckets_with_region():
    mock_s3 = MagicMock()
    mock_s3.list_buckets.return_value = {
        "Buckets": [
            {
                "Name": "test-bucket-with-location",
                "CreationDate": datetime(2020, 1, 2),
            }
        ]
    }
    mock_s3.get_bucket_location.return_value = {"LocationConstraint": "eu-west-3"}
    session = MagicMock()
    session.client.return_value = mock_s3

    buckets = harvest_buckets(session)
    bucket = S3Bucket(**buckets[0])
    assert bucket.id == "test-bucket-with-location"
    assert bucket.name == "test-bucket-with-location"
    assert bucket.bucketRegion == "eu-west-3"
    assert bucket.type == "s3"
    assert bucket.bucketArn == "arn:aws:s3:::test-bucket-with-location"
    assert bucket.creationDate == datetime(2020, 1, 2)

def test_harvest_roles():
    mock_iam = MagicMock()
    mock_iam.list_roles.return_value = {
        "Roles": [
            {
                "Arn": "arn:aws:iam::123456789012:role/TestRole",
                "RoleName": "TestRole",
                "RoleId": "ROLEID",
                "CreateDate": datetime(2021, 1, 1),
                "Path": "/",
                "RoleLastUsed": {"LastUsedDate": datetime(2022, 1, 1)}
            }
        ]
    }
    mock_iam.list_role_tags.return_value = {"Tags": [
        {"Key": "env", "Value": "prod"}
    ]}
    mock_iam.list_role_policies.return_value = {"PolicyNames": ["InlinePolicy"]}

    session = MagicMock()
    session.client.return_value = mock_iam

    roles = harvest_roles(session)
    role = IAMRole(**roles[0])
    assert role.id == "arn:aws:iam::123456789012:role/TestRole"
    assert role.type == "role"
    assert role.roleName == "TestRole"
    assert role.roleId == "ROLEID"
    assert role.createDate == datetime(2021, 1, 1)
    assert role.path == "/"
    assert role.roleLastUsed == datetime(2022, 1, 1)
    assert role.tags == [{"Key": "env", "Value": "prod"}]
    assert role.inlinePoliciesNames == ["InlinePolicy"]

def test_harvest_roles_empty():
    mock_iam = MagicMock()
    mock_iam.list_roles.return_value = {"Roles": []}
    session = MagicMock()
    session.client.return_value = mock_iam

    roles = harvest_roles(session)
    assert roles == []

def test_harvest_buckets_empty():
    mock_s3 = MagicMock()
    mock_s3.list_buckets.return_value = {"Buckets": []}
    session = MagicMock()
    session.client.return_value = mock_s3

    buckets = harvest_buckets(session)
    assert buckets == []

def test_harvest_buckets_updates():
    mock_s3 = MagicMock()
    # Original bucket data
    mock_s3.list_buckets.return_value = {
        "Buckets": [
            {
                "Name": "my-bucket",
                "CreationDate": datetime(2020, 1, 1),
            }
        ]
    }
    mock_s3.get_bucket_location.return_value = {"LocationConstraint": "us-west-1"}
    session = MagicMock()
    session.client.return_value = mock_s3

    buckets = harvest_buckets(session)
    bucket = S3Bucket(**buckets[0])
    assert bucket.bucketRegion == "us-west-1"
    assert bucket.name == "my-bucket"
    assert bucket.creationDate == datetime(2020, 1, 1)

    # Simulate bucket region changed (creationDate remains same)
    mock_s3.list_buckets.return_value = {
        "Buckets": [
            {
                "Name": "my-bucket",
                "CreationDate": datetime(2020, 1, 1),  # same creation date
            }
        ]
    }
    mock_s3.get_bucket_location.return_value = {"LocationConstraint": "eu-central-1"}
    buckets_updated = harvest_buckets(session)
    updated_bucket = S3Bucket(**buckets_updated[0])
    assert updated_bucket.bucketRegion == "eu-central-1"
    assert updated_bucket.creationDate == datetime(2020, 1, 1)

def test_harvest_roles_updates():
    mock_iam = MagicMock()
    # Original role data
    mock_iam.list_roles.return_value = {
        "Roles": [
            {
                "Arn": "arn:aws:iam::123456789012:role/MyRole",
                "RoleName": "MyRole",
                "RoleId": "ROLEID123",
                "CreateDate": datetime(2021, 1, 1),
                "Path": "/",
                "RoleLastUsed": {"LastUsedDate": datetime(2021, 12, 31)},
            }
        ]
    }
    mock_iam.list_role_tags.return_value = {"Tags": [{"Key": "env", "Value": "dev"}]}
    mock_iam.list_role_policies.return_value = {"PolicyNames": ["PolicyA"]}

    session = MagicMock()
    session.client.return_value = mock_iam

    roles = harvest_roles(session)
    role = IAMRole(**roles[0])
    assert role.roleName == "MyRole"
    assert role.tags == [{"Key": "env", "Value": "dev"}]
    assert role.inlinePoliciesNames == ["PolicyA"]

    # Simulate updated role data (changed path, last used date and tags)
    mock_iam.list_roles.return_value = {
        "Roles": [
            {
                "Arn": "arn:aws:iam::123456789012:role/MyRole",
                "RoleName": "MyRole",
                "RoleId": "ROLEID123",
                "CreateDate": datetime(2021, 1, 1),
                "Path": "/updated",
                "RoleLastUsed": {"LastUsedDate": datetime(2022, 1, 1)},
            }
        ]
    }
    mock_iam.list_role_tags.return_value = {"Tags": [{"Key": "env", "Value": "prod"}]}
    mock_iam.list_role_policies.return_value = {"PolicyNames": ["PolicyB"]}

    roles_updated = harvest_roles(session)
    updated_role = IAMRole(**roles_updated[0])
    assert updated_role.path == "/updated"
    assert updated_role.roleLastUsed == datetime(2022, 1, 1)
    assert updated_role.tags == [{"Key": "env", "Value": "prod"}]
    assert updated_role.inlinePoliciesNames == ["PolicyB"]
