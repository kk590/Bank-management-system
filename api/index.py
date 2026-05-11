import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv

# Fix imports for Vercel
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

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

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Go one level up to find static and templates
ROOT_DIR = os.path.dirname(BASE_DIR)
STATIC_DIR = os.path.join(ROOT_DIR, "static")
TEMPLATES_DIR = os.path.join(ROOT_DIR, "templates")

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=TEMPLATES_DIR)

app.include_router(auth_router.router, prefix="/api/auth", tags=["Auth"])
app.include_router(user_router.router, prefix="/api/users", tags=["Users"])
app.include_router(account_router.router, prefix="/api/accounts", tags=["Accounts"])
app.include_router(transaction_router.router, prefix="/api/transactions", tags=["Transactions"])
app.include_router(admin_router.router, prefix="/api/admin", tags=["Admin"])

@app.on_event("startup")
async def startup_event():
    try:
        await ping_db()
        await ensure_indexes()
    except Exception as e:
        print(f"[startup] DB init warning: {e}")

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
