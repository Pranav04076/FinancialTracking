import os
import shutil
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from sqlalchemy.orm import Session

from app.db import get_db
from app.dependencies import get_current_user
from app.models import User
from app.services.csv_parser import parse_csv
from app.services.pdf_parser import parse_pdf

router = APIRouter(prefix = "/upload", tags=['upload'])

UPLOAD_DIR = "uploads/temp"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload_csv")
def upload_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    filename = file.filename.lower()

    if not filename.endswith(".csv"):
        raise HTTPException(
            status_code=400,
            detail="Only CSV files are accepted"
        )

    file_path = f"{UPLOAD_DIR}/{current_user.id}_{file.filename}"

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        inserted, skipped = parse_csv(file_path, current_user.id, db)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    finally:
        os.remove(file_path)

    return {
        "message": "File imported successfully",
        "transactions_inserted": inserted,
        "transactions_skipped": skipped
    }

@router.post("/upload_pdf")
def upload_pdf(file: UploadFile= File(...),
               db: Session = Depends(get_db),
               current_user : User = Depends(get_current_user)):
    
    filename = file.filename.lower()

    if not filename.endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only pdf files are accepted"
        )

    file_path = f"{UPLOAD_DIR}/{current_user.id}_{file.filename}"

    with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

    try:
        inserted, skipped = parse_pdf(file_path, current_user.id, db)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process PDF: {str(e)}"
        )

    finally:
         if os.path.exists(file_path):
            os.remove(file_path)

    return {"message": "file imported successfully",
            "Inserted": inserted,
            "Skipped": skipped}