import os
import shutil
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from sqlalchemy.orm import Session

from app.db import get_db
from app.dependencies import get_current_user
from app.models import User
from app.services.parsers.csv_parser import parse_csv
from app.services.parsers.pdf_parser import parse_pdf

from app.services.route_services.upload_service import upload_csv, upload_pdf

router = APIRouter(prefix = "/upload", tags=['upload'])

@router.post("/upload_csv")
def upload_csv_route(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return upload_csv(current_user.id, file, db)

@router.post("/upload_pdf")
def upload_pdf_route(file: UploadFile= File(...),
               db: Session = Depends(get_db),
               current_user : User = Depends(get_current_user)):
    
    return upload_pdf(current_user.id, file, db)