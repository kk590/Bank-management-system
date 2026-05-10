import os

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv

from database import ensure_indexes, ping_db
from routers import account_router, admin_router, auth_router, transaction_router, user_router

load_dotenv()

app = FastAPI(title="Aureum Private Bank API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("static/css", exist_ok=True)
os.makedirs("static/js", exist_ok=True)
os.makedirs("templates", exist_ok=True)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

app.include_router(auth_router.router, prefix="/api/auth", tags=["Auth"])
app.include_router(user_router.router, prefix="/api/users", tags=["Users"])
app.include_router(account_router.router, prefix="/api/accounts", tags=["Accounts"])
app.include_router(transaction_router.router, prefix="/api/transactions", tags=["Transactions"])
app.include_router(admin_router.router, prefix="/api/admin", tags=["Admin"])


@app.on_event("startup")
async def startup_event():
    await ping_db()
    await ensure_indexes()


@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/dashboard")
async def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})


@app.get("/admin")
async def admin_dashboard(request: Request):
    return templates.TemplateResponse("admin.html", {"request": request})


@app.get("/api/health")
async def health():
    return {"status": "ok"}
