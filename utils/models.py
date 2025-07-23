from datetime import date, datetime
from pydantic import BaseModel

class Account(BaseModel):
    id: str
    name: str
    accessKey: str
    secret: str # stored encrypted in the DB

class S3Bucket(BaseModel):
    id: str 
    type: str
    bucketArn: str
    bucketRegion: str
    creationDate: datetime
    name: str  

class IAMRole(BaseModel):
    id: str
    type: str
    createDate: date
    path: str
    roleId: str
    roleName: str
    roleLastUsed: date
    tags: list
    inlinePoliciesNames: list