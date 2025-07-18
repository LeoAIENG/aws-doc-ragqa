# aws-doc-ragqa
This repo contains all steps for deploying an application for Retrieval Augmented Generation Question Answering for AWS Documentation.

## Deploy Application:  

```bash
docker-compose up
```

## Research:  
path: research/  
Notebooks, data analysis, chunking, indexing and evaluation  

## Data Versioning (DVC):  
paths:  
- /data  
- /research/data  

Restore files:
```bash
uv sync
uv run dvc pull
```

## Unzip S3 Lambda Handler
Upload Zip to S3:
```bash
python ./scripts/upload_zip_to_s3.py
```

Deploy Lambda Function Unzip Handler:
```bash
chmod +x ./deployment/deploy.sh
./deployment/deploy.sh
```