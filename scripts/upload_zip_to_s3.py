import os
import sys
from pathlib import Path
from dotenv import load_dotenv

src_path = (Path.cwd() / "src").as_posix()
sys.path.append(src_path)

from utils.s3_utils import S3Utils
import config as cfg

load_dotenv()

bucket_name = "aws-doc-ragqa"
region_name = "us-east-2"
aws_access_key_id = os.environ["AWS_ACCESS_KEY_ID"]
aws_secret_access_key = os.environ["AWS_SECRET_ACCESS_KEY"]
s3_utils = S3Utils(
    bucket_name=bucket_name,
    region_name=region_name,
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key
)

file_name = "sagemaker_documentation.zip"
file_path = (cfg.path.data.raw / file_name).as_posix()


s3_utils.upload_file(file_path=file_path, s3_key=file_name)