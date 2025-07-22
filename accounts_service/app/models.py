from pydantic import BaseModel

class Account(BaseModel):
    id: str
    name: str
    access_key: str
    secret: str # stored encrypted in the DB