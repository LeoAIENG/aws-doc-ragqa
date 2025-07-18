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
