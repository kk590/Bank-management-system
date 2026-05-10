from contextlib import asynccontextmanager
from fastapi import FastAPI

@asynccontextmanager
async def lifespan(app: FastAPI):
    # connect to MongoDB here
    yield
    # close client here

app = FastAPI(lifespan=lifespan)

@app.get("/")
def root():
    return {"status": "ok"}
