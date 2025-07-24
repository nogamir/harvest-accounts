from datetime import date, datetime
from pydantic import BaseModel
from typing import Optional


class Account(BaseModel):
    id: str
    name: str
    accessKey: str
    secret: str # stored encrypted in the DB

class S3Bucket(BaseModel):
    id: str 
    type: str
    bucketArn: str
    bucketRegion: Optional[str]
    creationDate: datetime
    name: str  

class IAMRole(BaseModel):
    id: str
    type: str
    createDate: datetime
    path: str
    roleId: str
    roleName: str
    roleLastUsed: Optional[datetime]
    tags: list
    inlinePoliciesNames: list