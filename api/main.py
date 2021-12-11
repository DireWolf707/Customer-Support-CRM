from fastapi import FastAPI
from verify.otp import otp_router
from ticket.call import ticket_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"Hello": "World"}

app.include_router(otp_router)
app.include_router(ticket_router)

