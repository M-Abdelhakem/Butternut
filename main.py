from fastapi import FastAPI
from routers.login import login_router
from routers.upload_csv_data import upload_data_router
from routers.retrieve_csv_data import retrieve_data_router
# Add the StaticFiles package to serve static files
from fastapi.staticfiles import StaticFiles
from fastapi import File, UploadFile
from fastapi.responses import JSONResponse
import shutil


app = FastAPI()

app.include_router(login_router)
app.include_router(upload_data_router)
app.include_router(retrieve_data_router)

# Mount a directory containing static files to the app
app.mount("/static", StaticFiles(directory="static"), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app)

