import io
import uuid
from fastapi import APIRouter, Cookie, File, Form, HTTPException, Request, UploadFile
from fastapi.templating import Jinja2Templates
from database import DBManager
import os
from schemas.upload_csv import UploadCSV
import pandas as pd
import datetime
from urllib.request import urlopen

upload_data_router = APIRouter()
DB_Manager = DBManager()

parent_directory = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
templates_directory = os.path.join(parent_directory, "templates")
templates = Jinja2Templates(directory=templates_directory)


@upload_data_router.get("/upload-csv-data")
async def upload_file(request: Request, username: str = Cookie(None)):
    if not username:
        raise HTTPException(status_code=401, detail="Unauthorized access")

    return templates.TemplateResponse(
        "upload_csv_data.html", {"request": request, "username": username}
    )


@upload_data_router.post("/upload-csv-data")
async def upload_file(
    file: UploadFile = File(None), url: str = Form(None), username: str = Cookie(None)
):
    if url:
        # Fetch file from URL
        df = pd.read_csv(url)
        file_name = url.split("/")[-1]  # Extract file name from URL
    elif file:
        # Process file upload
        contents = await file.read()  # Read the contents of the file
        df = pd.read_csv(
            io.BytesIO(contents)
        )  # Use io.BytesIO to convert bytes to file-like object
        file_name = file.filename
    else:
        raise HTTPException(
            status_code=400, detail="Either file or URL must be provided"
        )

    # Save the file data to the database
    file_data = df.to_dict(orient="records")
    upload_date = datetime.datetime.now()
    upload_id = str(uuid.uuid4())  # Generate a unique upload ID
    upload_record = UploadCSV(
        user_id=username,
        file_name=file_name,
        file_data=file_data,
        upload_date=upload_date,
        upload_id=upload_id,
    )

    # Save the upload record to the database
    DB_Manager.insert_upload_record(upload_record.model_dump())

    return {"message": "Data uploaded successfully!"}


