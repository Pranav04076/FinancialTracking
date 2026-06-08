import pdfplumber
from datetime import datetime

from app.services.banks.SBI import parse_sbi
from app.services.banks.HDFC import parse_hdfc
from app.services.banks.IDFC import parse_idfc
from app.services.banks.PNB import parse_pnb
from app.services.banks.FEDERAL import parse_federal


def detect_bank(file_path: str)->str:
    with pdfplumber.open(file_path) as pdf:
        text = pdf.pages[0].extract_text() or ""
        print(text)
        text = text.upper()

        if "FEDERAL" in text:
            return "FEDERAL"
        
        if "HDFC" in text:
            return "HDFC"
        
        if "IDFC" in text:
            return "IDFC"
        
        if "PUNJAB" and "NATIONAL" in text:
            return "PNB"
        
        if "STATE BANK OF INDIA" in text:
            return "SBI"
        
        raise ValueError("Bank Not Supported")

def parse_pdf(file_path: str, user_id, db):

    bank = detect_bank(file_path)
    # print(bank)
    if bank == "SBI":
        return parse_sbi(file_path, user_id, db)
    
    if bank=="HDFC":
        return parse_hdfc(file_path, user_id, db)
    
    if bank == "IDFC":
        return parse_idfc(file_path, user_id, db)
    
    if bank== "PNB":
        return parse_pnb(file_path, user_id, db)
    
    if bank == "FEDERAL":
        return parse_federal(file_path, user_id, db)
    
    raise ValueError("Unsupported Bank")