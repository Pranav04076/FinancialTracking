import pdfplumber
from datetime import datetime

def get_mode(description: str) -> str:
    description = description.upper()

    if "UPI" in description:
        return "UPI"

    if "NEFT" in description:
        return "NEFT"

    if "IMPS" in description:
        return "IMPS"

    if "RTGS" in description:
        return "RTGS"

    if "ATM" in description:
        return "ATM"

    if "ACH" in description:
        return "ACH"

    if "POS" in description:
        return "POS"

    if "CHEQUE" in description or "CHQ" in description:
        return "CHEQUE"

    if "CASH" in description:
        return "CASH"

    return "OTHER"

def parse_date(date_str: str):
    formats = [
        "%d-%m-%y",
        "%d-%m-%Y",
        "%d/%m/%y",
        "%d/%m/%Y",
        "%d-%b-%Y"
    ]

    for fmt in formats:
        try:
            return datetime.strptime(date_str.strip(), fmt).date()
        except ValueError:
            pass

    raise ValueError(f"Unsupported date format: {date_str}")

def extract_tables(file_path: str):
    rows=[]

    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()

            for table in tables:
                rows.extend(table)

    return rows