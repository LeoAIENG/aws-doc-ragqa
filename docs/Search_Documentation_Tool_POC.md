# Search Documentation Tool POC

Proof-of-Concept to develop an application for question answering based on retrieval augmented generation (RAG-QA) for AWS documentation.

## REFERENCES

[ML Engineer Tech Assessment](https://www.notion.so/ML-Engineer-Tech-Assessment-22d88a66bf1f80d4bf4bd0e61bd75a69?pvs=21)

[sagemaker_documentation.zip](sagemaker_documentation.zip)

---

## BUSINESS REQUIREMENTS

### Mandatory

- Search AWS Documentation Tool
- Reduce time of developers searching
- Reduce questions between developers
- Deliver the most updated information
- POC (Business Presentation)
- Handle Sensitive Documentation
- Data Geo Restrictions (US)
- Question for POC:
    - What is SageMaker?
    - What are all AWS regions where SageMaker is available?
    - How to check if an endpoint is KMS encrypted?
    - What are SageMaker Geospatial capabilities?
    

### Optional (nice-to-have)

- Point to the response source
- Point to others relevant documents to response

---

## TECHNICAL REQUIREMENTS

### Mandatory

- Application/API
- RAG-QA
- Prototyping/Demo
- Fast-pace development
- Reproducible Pattern
- Fast Search
- Scalable Database
- Evaluation
- Tests

### Optional (nice-to-have)

- Present Reference Document
- Present Relevant Documents to Subject

---

## PROPOSED APPLICATION

**Data Versioning:** AWS S3

**Indexing:** Qdrant (Speed) / ChromaDB (Quickly Develop / Prototyping)

**App:** FastAPI / Gradio

**LLM: Llamaindex (Bedrock / Gemini)**

**Tests:** Pytest

Evaluation: **Llamaindex /** W&B Weave

**Observability:** W&B Weave

**Deployment:** AWS ECR / AWS EKS /  (AWS Lambda)

**Demo:**  Gradio

---

## TODO:

- Improve Chunking, Build index pipeline, recheck LLM and evaluation cycle
- Improve performance and refactor on app.py
- Implement application tests
- Implement CI/CD for AWS Lambda/ AWS ECR / AWS EKS
- Implement FastAPI for concurrent access
- Add more AWS documentation (out of scope of POC)

---

[]