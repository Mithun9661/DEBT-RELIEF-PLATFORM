# Ledger Relief — AI-Powered Debt Relief & Financial Recovery Platform

An AI-driven web application that helps borrowers manage debt, analyze
financial health, and generate settlement strategies. Built with
**React (Vite)**, **FastAPI**, **SQLite/SQLAlchemy**, and **Google Gemini AI**.

## What's included

- **Backend** (`/backend`) — FastAPI REST API
  - JWT authentication (register/login)
  - Loan/debt CRUD, scoped per user
  - Deterministic financial analysis: debt-to-income ratio, disposable income,
    a 0–100 financial health score, and risk flags
  - Heuristic settlement-percentage predictor (delinquency, loan type, lump-sum offers)
  - Gemini-powered negotiation strategy and negotiation letter generation
  - SQLite by default; swap `DATABASE_URL` for Postgres/MySQL in production
- **Frontend** (`/frontend`) — React + Vite single-page app
  - Login / registration
  - Dashboard with financial health "stamp," account list, risk flags
  - Loan management (add / view / delete accounts)
  - Settlement Predictor with AI negotiation-strategy generation
  - AI Letter Generator with tone selection and hardship context

## 1. Backend setup

```bash
cd backend
python3.11 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# Edit .env:
#   - Set SECRET_KEY to a long random string
#     (generate one with: python -c "import secrets; print(secrets.token_hex(32))")
#   - Set GEMINI_API_KEY to your key from https://aistudio.google.com/apikey

uvicorn app.main:app --reload
```

The API runs at `http://localhost:8000`. Interactive docs (Swagger UI) are at
`http://localhost:8000/docs`.

Tables are created automatically on first run (SQLite file `debt_relief.db`
in the `backend/` folder). For schema changes in production, introduce
Alembic migrations rather than relying on `create_all`.

## 2. Frontend setup

```bash
cd frontend
npm install
cp .env.example .env
# VITE_API_URL should point at your backend, e.g. http://localhost:8000

npm run dev
```

The app runs at `http://localhost:5173` and talks to the backend at the URL
in `VITE_API_URL`.

## 3. Using the app

1. Register an account (enter your monthly income/expenses — you can update
   these later).
2. Add your loans/credit accounts under **Loans**.
3. Visit the **Dashboard** to see your financial health score, debt-to-income
   ratio, and any risk flags.
4. Use **Settlement Predictor** to estimate a realistic settlement percentage
   for an account, and optionally generate an AI negotiation strategy.
5. Use **AI Letter Generator** to draft a settlement negotiation letter in a
   professional, firm, or empathetic tone.

## 4. Environment variables reference

### backend/.env
| Variable | Description |
|---|---|
| `SECRET_KEY` | Signing key for JWTs — must be kept secret in production |
| `ALGORITHM` | JWT signing algorithm (default `HS256`) |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token lifetime in minutes |
| `DATABASE_URL` | SQLAlchemy connection string |
| `GEMINI_API_KEY` | Your Google Gemini API key |
| `GEMINI_MODEL` | Gemini model name (default `gemini-2.0-flash`) |
| `FRONTEND_ORIGIN` | Allowed CORS origin for the frontend |

### frontend/.env
| Variable | Description |
|---|---|
| `VITE_API_URL` | Base URL of the backend API |

## 5. Security & production notes

- Replace the default `SECRET_KEY` before any real deployment.
- Passwords are hashed with bcrypt; never log or store plaintext passwords.
- All loan/settlement/letter endpoints are scoped to the authenticated user —
  no user can read or modify another user's data.
- For production, move off SQLite to a managed Postgres/MySQL instance, put
  the API behind HTTPS, and set `FRONTEND_ORIGIN` to your real domain (avoid
  wildcard CORS).
- This platform provides financial guidance and drafting tools — it does not
  replace advice from a licensed credit counselor, attorney, or financial
  advisor, and the app's AI-generated letters and strategies should be
  reviewed by the user before being sent to a creditor.

## 6. Project structure

```
debt-relief-platform/
├── backend/
│   ├── app/
│   │   ├── core/            # config, security, auth dependency
│   │   ├── routers/         # auth, users, loans, financial, settlement, letters
│   │   ├── services/        # financial_calculations.py, ai_service.py (Gemini)
│   │   ├── database.py
│   │   ├── models.py        # SQLAlchemy ORM models
│   │   ├── schemas.py       # Pydantic request/response schemas
│   │   └── main.py          # FastAPI app entrypoint
│   ├── requirements.txt
│   └── .env.example
└── frontend/
    ├── src/
    │   ├── api/              # axios client + endpoint functions
    │   ├── context/          # AuthContext
    │   ├── components/       # Layout, ProtectedRoute
    │   ├── pages/             # Login, Register, Dashboard, Loans, Predictor, Letters
    │   ├── App.jsx
    │   └── index.css / App.css
    ├── package.json
    └── .env.example
```
