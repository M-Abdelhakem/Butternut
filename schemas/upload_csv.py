import datetime
from typing import List
from pydantic import BaseModel


class UploadCSV(BaseModel):
    user_id: str
    file_name: str
    file_data: List[dict]
    upload_date: datetime.datetime
    upload_id: str
