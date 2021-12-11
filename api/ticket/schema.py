from pydantic import BaseModel,Field

class TextTicket(BaseModel):
    text : str
    ticket_id : str

class CallTicket(BaseModel):
    phone : str = Field(...,max_length=13,min_length=10)