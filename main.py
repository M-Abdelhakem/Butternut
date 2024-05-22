import os
from fastapi import FastAPI
from routers.login import login_router
from routers.upload_csv_data import upload_data_router
from routers.retrieve_csv_data import retrieve_data_router
from routers.email_sending import sending_emails_router
from fastapi.staticfiles import StaticFiles

app = FastAPI()

app.include_router(login_router)
app.include_router(upload_data_router)
app.include_router(retrieve_data_router)
app.include_router(sending_emails_router)

parent_directory = os.path.dirname(os.path.abspath(__file__))
static_directory = os.path.join(parent_directory, "static")
app.mount("/static", StaticFiles(directory=static_directory), name="static")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
