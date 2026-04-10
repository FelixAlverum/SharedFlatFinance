from pydantic import BaseModel, EmailStr

class UserBalance(BaseModel):
    email: EmailStr
    name: str
    amount: float

    class Config:
        from_attributes = True