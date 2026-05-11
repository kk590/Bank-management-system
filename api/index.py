from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def read_root():
    return {"message": "Hello World"}

# Remove any uvicorn.run() calls - Vercel handles this automatically
