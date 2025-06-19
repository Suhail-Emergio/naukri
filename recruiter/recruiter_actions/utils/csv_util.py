#################################  C S V  D A T A  F E T C H I N G  #################################
import csv, io
from .candidate_gen import candidate_creation
from django.http import HttpResponse

async def get_csv_data(file, job):
    text_file = io.TextIOWrapper(file, encoding='utf-8')
    reader = csv.reader(text_file.read().splitlines())
    header = [col.lower() for col in next(reader, None)]
    if "email" not in header:
        return False, {"message": "Email column not found in CSV"}
    for row in reader:
        email_index = header.index("email")
        email = row[email_index]
        await candidate_creation(email, job)
    return True, {"message": "CSV data processed successfully"}

async def create_csv(data):
    csv_buffer = io.StringIO()
    csv_writer = csv.writer(csv_buffer)

    data = data.get("applications", [])
    # Write the header row
    if data and len(data) > 0:
        headers = data[0].keys()
        csv_writer.writerow(headers)

    # Write the data rows
    for row in data:
        csv_writer.writerow(row.values())
    csv_buffer.seek(0)
    response = HttpResponse(
        content=csv_buffer.getvalue(),
        content_type="text/csv"
    )
    filename = "applications.csv"
    response.headers["Content-Disposition"] = f"attachment; filename={filename}"
    return response