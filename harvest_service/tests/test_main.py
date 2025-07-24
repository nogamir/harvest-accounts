import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))  # Adjust path to import from src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))  # Adjust path to import from src
from src import main

@patch("main.create_boto3_session")
@patch("main.harvest_roles")
@patch("main.harvest_buckets")
@patch("main.accounts_collection.find")
@patch("main.harvest_db")
def test_harvest_all_accounts(mock_db, mock_find, mock_buckets, mock_roles, mock_create_session):
    mock_find.return_value = [{"_id": "acc1", "accessKey": "k", "secret": "s", "name": "acc"}]
    mock_buckets.return_value = [{
        "id": "bucket1",
        "type": "s3",
        "bucketArn": "arn:aws:s3:::bucket1",
        "bucketRegion": "us-east-1",
        "creationDate": datetime(2020, 1, 1),
        "name": "bucket1",
    }]
    mock_roles.return_value = [{
        "id": "arn:aws:iam::123456789012:role/role1",
        "type": "role",
        "createDate": datetime(2021, 1, 1),
        "path": "/",
        "roleId": "roleid1",
        "roleName": "role1",
        "roleLastUsed": datetime(2022, 1, 1),
        "tags": [],
        "inlinePoliciesNames": ["policy1"],
    }]

    mock_coll_buckets = MagicMock()
    mock_coll_roles = MagicMock()
    mock_db.__getitem__.side_effect = lambda name: {
        "buckets": mock_coll_buckets,
        "roles": mock_coll_roles,
    }[name]

    main.harvest_all_accounts()

    mock_coll_buckets.delete_many.assert_called()
    mock_coll_roles.delete_many.assert_called()
    mock_coll_buckets.bulk_write.assert_called_once()
    mock_coll_roles.bulk_write.assert_called_once()


@patch("main.accounts_collection.find")
@patch("main.harvest_db")
def test_delete_buckets_and_roles_for_inactive_accounts(mock_db, mock_find):
    mock_find.return_value = []
    mock_coll_buckets = MagicMock()
    mock_coll_roles = MagicMock()
    mock_db.__getitem__.side_effect = lambda name: {
        "buckets": mock_coll_buckets,
        "roles": mock_coll_roles,
    }[name]

    main.harvest_all_accounts()

    mock_coll_buckets.delete_many.assert_called_once_with({"account_id": {"$nin": []}})
    mock_coll_roles.delete_many.assert_called_once_with({"account_id": {"$nin": []}})


@patch("main.create_boto3_session")
@patch("main.harvest_roles")
@patch("main.harvest_buckets")
@patch("main.accounts_collection.find")
@patch("main.harvest_db")
def test_delete_inactive_buckets_and_roles_for_active_account(mock_db, mock_find, mock_buckets, mock_roles, mock_create_session):
    account_id = "acc1"
    mock_find.return_value = [{
        "_id": account_id,
        "accessKey": "k",
        "secret": "s",
        "name": "acc",
    }]

    mock_buckets.return_value = [
        {
            "id": "bucket1",
            "type": "s3",
            "bucketArn": "arn:aws:s3:::bucket1",
            "bucketRegion": "us-east-1",
            "creationDate": datetime(2020, 1, 1),
            "name": "bucket1",
        },
        {
            "id": "bucket2",
            "type": "s3",
            "bucketArn": "arn:aws:s3:::bucket2",
            "bucketRegion": "us-west-2",
            "creationDate": datetime(2020, 2, 2),
            "name": "bucket2",
        },
    ]
    mock_roles.return_value = [
        {
            "id": "role1",
            "type": "role",
            "createDate": datetime(2021, 1, 1),
            "path": "/",
            "roleId": "roleid1",
            "roleName": "role1",
            "roleLastUsed": None,
            "tags": [],
            "inlinePoliciesNames": [],
        },
    ]

    mock_coll_buckets = MagicMock()
    mock_coll_roles = MagicMock()
    mock_db.__getitem__.side_effect = lambda name: {
        "buckets": mock_coll_buckets,
        "roles": mock_coll_roles,
    }[name]

    main.harvest_all_accounts()

    bucket_delete_filter = mock_coll_buckets.delete_many.call_args[0][0]
    role_delete_filter = mock_coll_roles.delete_many.call_args[0][0]

    assert bucket_delete_filter["account_id"] == account_id
    assert set(bucket_delete_filter["id"]["$nin"]) == {"bucket1", "bucket2"}

    assert role_delete_filter["account_id"] == account_id
    assert set(role_delete_filter["id"]["$nin"]) == {"role1"}

    mock_coll_buckets.bulk_write.assert_called_once()
    mock_coll_roles.bulk_write.assert_called_once()