from uuid import UUID
import os
import shutil
from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session
from app.services.parsers.csv_parser import parse_csv
from app.services.parsers.pdf_parser import parse_pdf

UPLOAD_DIR = "uploads/temp"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def upload_csv(
        user_id: UUID,
    file: UploadFile,
    db: Session):

    filename = file.filename.lower()

    if not filename.endswith(".csv"):
        raise HTTPException(
            status_code=400,
            detail="Only CSV files are accepted"
        )

    file_path = f"{UPLOAD_DIR}/{user_id}_{file.filename}"

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        inserted, skipped = parse_csv(file_path, user_id, db)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    finally:
        os.remove(file_path)

    return {
        "message": "File imported successfully",
        "transactions_inserted": inserted,
        "transactions_skipped": skipped
    }

def upload_pdf(
            user_id: UUID,
            file: UploadFile,
            db: Session):
    
    filename = file.filename.lower()

    if not filename.endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only pdf files are accepted"
        )

    file_path = f"{UPLOAD_DIR}/{user_id}_{file.filename}"

    with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

    try:
        inserted, skipped = parse_pdf(file_path, user_id, db)

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