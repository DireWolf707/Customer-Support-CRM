from pydantic import BaseModel,Field

class SendRequest(BaseModel):
    phone : str = Field(...,max_length=13,min_length=10)

class VerifyRequest(BaseModel):
    phone : str = Field(...,max_length=13,min_length=10)
    otp : str = Field(...,max_length=6,min_length=6)