#################################  C S V  D A T A  F E T C H I N G  #################################
import csv, io
from .candidate_gen import candidate_creation

async def get_csv_data(file, job):
    text_file = io.TextIOWrapper(file, encoding='utf-8')
    reader = csv.reader(text_file.read().splitlines())
    candidates = []
    header = [col.lower() for col in next(reader, None)]
    if "email" not in header:
        return False, {"message": "Email column not found in CSV"}
    for row in reader:
        email_index = header.index("email")
        email = row[email_index]
        candidate_creation(email, job)
    return True, {"message": "CSV data processed successfully"}