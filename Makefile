#################################################################################
# GLOBALS                                                                       #
#################################################################################

PROJECT_NAME = aws-doc-ragqa
PYTHON_VERSION = 3.11
PYTHON_INTERPRETER = python

#################################################################################
# COMMANDS                                                                      #
#################################################################################


## Install Python dependencies
.PHONY: requirements
requirements:
	uv sync

## Delete all compiled Python files
.PHONY: clean
clean:
	find . -type f -name "*.py[co]" -delete
	find . -type d -name "__pycache__" -delete

## Lint using ruff (use `make format` to do formatting)
.PHONY: lint
lint:
	uv run ruff check --fix
	uv run ruff check

## Format source code with ruff
.PHONY: format
format:
	uv run ruff format --check
	uv run ruff format

## Upload Data to storage system
.PHONY: sync_data_up
sync_data_up:
	uv sync
	uv run dvc pull

# Upload Docs to S3 Zipped
.PHONY: upload_docs_zip_to_s3
upload_docs_zip_to_s3:
	python ./scripts/upload_zip_to_s3.py


# Deploy Lambda function for Unzip File on S3
.PHONY: deploy_unzip_lambda
deploy_unzip_lambda:
	chmod +x ./deployment/deploy.sh
	./deployment/deploy.sh