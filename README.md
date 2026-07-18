# 💰 Financial Tracking System (https://financial-tracking-njm9zucvs-pranav04076s-projects.vercel.app/)

A backend REST API for personal finance management. It ingests bank statements (CSV / PDF), auto-categorizes transactions with a machine-learning model, and exposes budgeting, analytics, and AI-generated insights — all behind JWT-secured endpoints.

---

## ✨ Features

- **Authentication & Authorization** — JWT access + refresh tokens, password hashing via `pwdlib` (bcrypt).
- **Transaction Management** — Full CRUD for income/expense transactions, scoped to the authenticated user.
- **Bank Statement Ingestion** — Upload CSV or PDF bank statements; parsers normalize the data into the `transactions` table.
- **Automatic Categorization** — A scikit-learn model (`model.pkl`) predicts the spending category (Food, Travel, Bills, etc.) from the narration text, with a confidence score.
- **Budgets** — Per-category monthly limits with status tracking (spent vs. limit).
- **Analytics** — Balance, monthly income/expense/net, largest transactions, category breakdown, spending trends, monthly savings, and date-range queries.
- **AI Insights** — Uses the Groq LLM API to generate natural-language financial insights from a user's transaction history.
- **Request Logging** — Custom middleware logs every request (method, path, status, latency).
- **Data Validation** — Pydantic schemas enforce business rules (e.g. amount > 0, no future transaction dates).

---

## 🏗️ Architecture

```
FinancialTracking/
├── main.py                        # Uvicorn entry point
├── pyproject.toml                 # Dependencies (uv)
├── .env                           # Secrets (DB URL, JWT key, Groq key)
├── app/
│   ├── app.py                     # FastAPI app, lifespan, middleware, router mounting
│   ├── auth.py                    # Password hashing, JWT helpers
│   ├── db.py                      # SQLAlchemy engine, session factory, get_db()
│   ├── dependencies.py            # get_current_user (OAuth2 bearer)
│   ├── logger.py                  # Custom logger
│   ├── models.py                  # SQLAlchemy ORM: User, Transaction, Budget
│   ├── schemas.py                 # Pydantic request/response models
│   ├── routes/                    # Thin FastAPI routers (auth, transaction, analytics, upload, budget)
│   ├── services/
│   │   ├── route_services/        # Business logic per route
│   │   ├── parsers/               # CSV / PDF parsers, AI insights
│   │   └── banks/                 # Bank-specific parser logic
│   ├── ML/
│   │   ├── model.pkl              # Trained scikit-learn classifier
│   │   ├── predictor.py           # predict_category() inference
│   │   └── update_confidence.py   # Re-score existing transactions
│   └── notebooks/                 # EDA / model training notebooks
├── tests/                         # Test suite
├── uploads/                       # Uploaded statement files
└── logs/                          # Application logs
```

**Layered design:** `routes/` (HTTP) → `services/route_services/` (business logic) → `models.py` (persistence). ML inference and AI insights are isolated in `app/ML` and `app/services/parsers/insights.py` respectively.

---

## 🛠️ Tech Stack

| Layer            | Tools |
|------------------|-------|
| API framework    | FastAPI + Uvicorn |
| ORM / DB         | SQLAlchemy + PostgreSQL (psycopg2) |
| Auth             | `python-jose` (JWT), `pwdlib` (bcrypt) |
| Validation       | Pydantic v2 |
| ML               | scikit-learn, joblib |
| Data processing  | pandas, pdfplumber, openpyxl |
| AI / LLM         | Groq SDK |
| Migrations       | Alembic |
| Package manager  | [uv](https://docs.astral.sh/uv/) |

---

## 🚀 Getting Started

### Prerequisites

- Python **3.13+**
- PostgreSQL **14+** running locally (or any reachable instance)
- [uv](https://docs.astral.sh/uv/) installed

### 1. Clone & install

```bash
git clone <your-repo-url>
cd FinancialTracking
uv sync
```

### 2. Configure environment

Create a `.env` file in the project root:

```env
DATABASE_URL=postgresql://<user>:<password>@localhost:5432/FinanceTracker
SECRET_KEY=<a-long-random-string>
ACCESS_TOKEN_EXPIRE_MINUTES=3000
GROQ_API_KEY=<your-groq-api-key>
```

> ⚠️ **Never commit `.env`.** It's already in `.gitignore`.

### 3. Initialize the database

Tables are auto-created on startup via `Base.metadata.create_all(bind=engine)` in the FastAPI lifespan. For production, swap in Alembic migrations:

```bash
alembic init alembic
alembic revision --autogenerate -m "init"
alembic upgrade head
```

### 4. Run the server

```bash
uv run python main.py
```

Or directly:

```bash
uvicorn app.app:app --host 0.0.0.0 --port 8000 --reload
```

API is now live at **http://localhost:8000** — interactive docs at **/docs** (Swagger UI) and **/redoc**.

---

## 📡 API Overview

| Method | Endpoint                                 | Auth | Description |
|--------|------------------------------------------|------|-------------|
| POST   | `/auth/register`                         | —    | Create a new user |
| POST   | `/auth/login/`                           | —    | Obtain access + refresh tokens (OAuth2 password flow) |
| POST   | `/auth/refresh`                          | —    | Rotate access token |
| POST   | `/auth/logout`                           | ✅   | Invalidate refresh token |
| POST   | `/transactions/create_transaction`       | ✅   | Add a transaction (auto-categorized by ML) |
| GET    | `/transactions/get_Transactions`         | ✅   | List with pagination (`limit`, `offset`) |
| GET    | `/transactions/balance`                  | ✅   | Current credit − debit |
| GET    | `/transactions/get_transaction/{id}`     | ✅   | Fetch one |
| PUT    | `/transactions/update_transaction/{id}`  | ✅   | Partial update |
| DELETE | `/transactions/delete_transaction/{id}`  | ✅   | Remove |
| POST   | `/upload/upload_csv`                     | ✅   | Ingest a CSV bank statement |
| POST   | `/upload/upload_pdf`                     | ✅   | Ingest a PDF bank statement |
| GET    | `/analytics/balance/`                    | ✅   | Total balance |
| GET    | `/analytics/total_debit/`                | ✅   | Total spent |
| GET    | `/analytics/total_credit/`               | ✅   | Total earned |
| GET    | `/analytics/monthly_income/`             | ✅   | Income for a (month, year) |
| GET    | `/analytics/monthly_expense/`            | ✅   | Spend for a (month, year) |
| GET    | `/analytics/monthly_net/`                | ✅   | Net (income − expense) |
| GET    | `/analytics/largest_expense`             | ✅   | Biggest single expense in a month |
| GET    | `/analytics/largest_income`              | ✅   | Biggest single income in a month |
| GET    | `/analytics/avg_transaction_amount/`     | ✅   | Mean transaction size |
| GET    | `/analytics/transactions-between/`       | ✅   | Filter by `start_date` / `end_date` |
| GET    | `/analytics/monthly_savings`             | ✅   | Savings for a month |
| GET    | `/analytics/recent_transactions`         | ✅   | Latest N transactions |
| GET    | `/analytics/category-breakdown`          | ✅   | Spend grouped by category |
| GET    | `/analytics/spending_trends/`            | ✅   | Month-by-month spend for a year |
| GET    | `/analytics/insights`                    | ✅   | AI-generated insights (Groq) |
| POST   | `/budget/add_budget`                     | ✅   | Set a monthly limit per category |
| GET    | `/budget/get_budget`                     | ✅   | List your budgets |
| PUT    | `/budget/update_budget/{category}`       | ✅   | Update a limit |
| DELETE | `/budget/delete_budget/{category}`       | ✅   | Remove a budget |
| GET    | `/budget/status`                         | ✅   | Spent vs. limit, by category |

✅ = requires `Authorization: Bearer <access_token>` header.

### Example: register → login → add a transaction

```bash
# 1. Register
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"pranav","email":"p@x.com","password":"S3cret!pw"}'

# 2. Login (returns access_token + refresh_tokens)
curl -X POST http://localhost:8000/auth/login/ \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=p@x.com&password=S3cret!pw"

# 3. Add a transaction
curl -X POST http://localhost:8000/transactions/create_transaction \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
        "type": "DEBIT",
        "mode": "UPI",
        "amount": 425.50,
        "valueDate": "2026-07-14",
        "narration": "Swiggy order"
      }'
```

The narration is run through the ML model — the response includes the predicted `category` and `confidence`.

---

## 🤖 Machine Learning

- **Task:** Multi-class text classification — predict a transaction's spending category from its narration.
- **Training data:** `TestDataSet/` and `app/bank_statements.csv` (see the notebooks in `app/notebooks/` for EDA / training).
- **Model artifact:** `app/ML/model.pkl` (loaded once at import time).
- **Inference:** `app/ML/predictor.predict_category(narration)` returns `{"category": ..., "confidence": ...}`. If confidence < 0.1, the category falls back to `"Other"`.
- **Re-scoring:** `python -m app.ML.update_confidence` to recompute categories for existing rows after a model upgrade.

---

## 🔒 Security Notes

- Passwords are hashed with `pwdlib`'s recommended algorithm (bcrypt-family).
- Tokens use HS256 JWTs; the `SECRET_KEY` must be a high-entropy string in production.
- All write endpoints and analytics are owner-scoped through `get_current_user` — users can only see their own data.

---

## 🔐 Environment Setup

Copy the example env file and fill in your own values:

```bash
cp .env.example .env
```

`.env` is already in `.gitignore` and is **never** committed. Generate a strong `SECRET_KEY` with:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

If you fork this project, rotate every credential in your own `.env` — never reuse the values from a clone.

---

## 🧪 Testing

```bash
uv run pytest
```

A minimal `app/ML/test_predictor.py` sanity-checks the inference pipeline.

---

## 🗺️ Roadmap

See `Financial Tracking System Roadmap.pdf` for the full plan. Highlights:

- Alembic migrations for production deployments
- Recurring-transaction detection
- Pluggable bank-specific parsers
- Frontend dashboard (separate repo / `streamlit` is already a dependency for prototyping)
- Anomaly / fraud detection on top of the existing model

---

## 📄 License

Add a license of your choice (e.g. MIT) before going public.

---

## 🙋 Author

Built by **Pranav**. Pull requests welcome.
