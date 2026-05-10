# Aureum Private Bank Management System

FastAPI + MongoDB backend connected to the included premium banking UI.

## What it includes
- JWT authentication
- Customer and admin roles
- Create bank accounts
- Deposit, withdraw, and transfer funds
- Transaction history
- Admin account/user/transaction management
- MongoDB persistence

## Setup
1. Install MongoDB and make sure it is running.
2. Copy `.env.example` to `.env` and edit values if needed.
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Seed demo data:
   ```bash
   python seed.py
   ```
5. Run the app:
   ```bash
   uvicorn main:app --reload
   ```
6. Open:
   - `http://127.0.0.1:8000` for the UI
   - `http://127.0.0.1:8000/docs` for API docs

## Demo credentials
- Admin: `admin` / `admin123`
- Customer: `johndoe` / `password123`
