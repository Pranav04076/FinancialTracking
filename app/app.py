from fastapi import FastAPI, HTTPException, File, UploadFile, Form, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager
from sqlalchemy import select
from app.Logic import createExcel
from app.db import engine, Base
from app.models import User, Transaction
from app.schemas import TransactionType
from app.routes import auth, transaction, analytics, upload, budget
import shutil
import os
import uuid
import tempfile
from openpyxl import load_workbook, Workbook
import pandas as pd
from datetime import date
from app.db import DATABASE_URL
import time
from app.logger import logger 

latest_file = None

def calculate_totals():

    if latest_file is None:
        raise HTTPException(
            status_code=404,
            detail="No file uploaded yet"
        )
    
    debit = pd.read_excel(latest_file, sheet_name='DEBIT')
    credit = pd.read_excel(latest_file, sheet_name='CREDIT')

    total_debit = debit['amount'].sum()
    total_credit = credit['amount'].sum()
    
    return total_debit, total_credit


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup


    #print(DATABASE_URL)

    Base.metadata.create_all(bind=engine)

    yield

app = FastAPI(lifespan=lifespan)

# CORS — required so the Next.js frontend (localhost:3000 in dev,
# *.vercel.app in production) can call this API from a browser.
# When you get your real Vercel domain, add it to allow_origins below.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://*.vercel.app",
        # "https://finance-frontend.vercel.app",  # ← add your prod domain here
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth.router)
app.include_router(transaction.router)
app.include_router(analytics.router)
app.include_router(upload.router)
app.include_router(budget.router)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.time()
    response = await call_next(request)

    duration = round(time.time() - start, 3)
    logger.info(f"{request.method} {request.url.path} | {response.status_code} | {duration}s")
    return response

