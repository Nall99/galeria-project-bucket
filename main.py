from presignedURL_upload import create_presigned_post
from fastapi.middleware.cors import CORSMiddleware
from model.uploadRequest import UploadRequest
from fastapi import FastAPI
from botocore.config import Config
import boto3
import uuid
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:4200/'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

def build_s3_client(endpoint_url):
    return boto3.client('s3',
                        endpoint_url=endpoint_url,
                        aws_access_key_id=os.getenv('MINIO_KEY_ACCESS'),
                        aws_secret_access_key=os.getenv('MINIO_KEY_SECRET'),
                        region_name='us-esat-1',
                        config=Config(
                            signature_version='s3v4',
                            s3={'addressing_style': 'path'}
                        ))

internal_client = build_s3_client(os.getenv("MINIO_ENDPOINT"))
public_client = build_s3_client(
    os.getenv('MINIO_PUBLIC_ENDPOINT', os.getenv('MINIO_ENDPOINT'))
)

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/upload-url")
def get_upload_url(request: UploadRequest):
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

@app.get("/photos")
def list_photos():

    response = internal_client.list_objects_v2(Bucket=os.getenv("MINIO_BUCKET_NAME"))

    if 'Contents' not in response:
        return {"photos": []}

    photos = []
    for obj in response['Contents']:
        url = public_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': os.getenv("MINIO_BUCKET_NAME"), 'Key': obj['Key']},
            ExpiresIn=300
        )

        photos.append({
            "key": obj['Key'],
            "url": url,
            "last_modified": obj['LastModified'].isoformat()
        })

    photos.sort(key=lambda p: p['last_modified'], reverse=True)
    return {"photos": photos}
