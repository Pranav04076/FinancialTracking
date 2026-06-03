from fastapi import FastAPI, HTTPException, File, UploadFile, Form, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager
from sqlalchemy import select
from app.Logic import createExcel
import shutil
import os
import uuid
import tempfile
from openpyxl import load_workbook, Workbook
import pandas as pd

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


app = FastAPI()


@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    global latest_file
    temp_dir = None
    try:
        if not file.filename.endswith(('.csv', '.xlsx', '.pdf')):
            raise HTTPException(status_code=400, detail="Invalid file type. Only CSV, XLSX, and PDF files are allowed.")
        
        temp_dir =tempfile.mkdtemp()
        out_dir = "C:/Users/LENOVO/OneDrive/Desktop/FinancialTracking/"
        file_path = os.path.join(temp_dir, file.filename)
        output_file = os.path.join(out_dir, "expense.xlsx")
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        #print("Before Create Excel", flush=True)
        excel_file = createExcel(file_path, output_file)
        latest_file = output_file
        #print("After Create Excel", flush = True)
        os.remove(file_path)
        return {"message": "File uploaded and processed successfully."}
    
    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(status_code=500, detail = str(e))
    
    finally: 
        #if temp_dir:
        #    shutil.rmtree(temp_dir, ignore_errors=True)

        await file.close()

@app.get('/Total_Debit/')
async def get_Debit():
    debit,_ = calculate_totals()
    return {'Total Debit': debit}

@app.get('/Total_Credit/')
async def get_Credit():
    _,credit = calculate_totals()
    return {'Total Credit': credit}

@app.get("/Balance/")
async def get_balance():
    debit, credit= calculate_totals()    

    total_balance = credit-debit
    return {'Balance': total_balance}


