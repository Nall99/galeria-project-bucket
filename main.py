from presignedURL_upload import create_presigned_post
from fastapi.middleware.cors import CORSMiddleware
from model.uploadRequest import UploadRequest
from fastapi import FastAPI
import uuid
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:4200'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/upload-url")
def get_upload_url(request: UploadRequest):
    # Gera um nome único, mas preserva extensão original
    extensao = os.path.splitext(request.filename)[1]
    object_name = f"{uuid.uuid4()}{extensao}"

    presigned_data = create_presigned_post(
        bucket_name=os.getenv("MINIO_BUCKET_NAME"),
        object_name=object_name,
        expiration=300 # 5 minutos para completar o upload
    )

    if presigned_data is None:
        return {"error": "Não foi possível gerar a URL de upload"}
    return presigned_data
