# aws-doc-ragqa
This repo contains all steps for deploying an application for Retrieval Augmented Generation Question Answering for AWS Documentation.

## Deploy Application:  

```bash
docker-compose up
```
link: http://localhost:7860/

## Research:  
path: research/  
Notebooks, data analysis, chunking, indexing and evaluation  

## Data Versioning (DVC):  
paths:  
- /data  
- /research/data  

Restore files:
```bash
make sync_data_up
```

## Unzip S3 Lambda Handler
Upload Zip to S3:
```bash
make upload_docs_zip_to_s3
```

Deploy Lambda Function Unzip Handler:
```bash
make deploy_unzip_lambda
```

## Project Notion Documentation:
Ask for access link!  
[DOCS LINK](docs/Search_Documentation_Tool_POC.md)  
[TIMELINE LINK](images/timeline.png)