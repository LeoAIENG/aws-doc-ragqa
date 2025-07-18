import boto3
import os
import json
import config as cfg
from pathlib import Path
from botocore.exceptions import ClientError
from typing import List, Optional, Any

class S3Utils:
    def __init__(self, bucket_name: str, region_name: Optional[str] = None, aws_access_key_id: Optional[str] = None, aws_secret_access_key: Optional[str] = None):
        self.bucket_name = bucket_name
        self.s3 = boto3.client(
            's3',
            region_name=region_name,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key
        )

    def upload_file(self, file_path: str, s3_key: str, extra_args: Optional[dict] = None) -> bool:
        """
        Uploads a file to S3.
        :param file_path: Local path to the file.
        :param s3_key: S3 object key.
        :param extra_args: Extra arguments for upload (e.g., ContentType).
        :return: True if upload succeeded, False otherwise.
        """
        try:
            self.s3.upload_file(file_path, self.bucket_name, s3_key, ExtraArgs=extra_args or {})
            return True
        except ClientError as e:
            print(f"Failed to upload {file_path} to {s3_key}: {e}")
            return False

    def upload_json(self, data: Any, s3_key: str, extra_args: Optional[dict] = None) -> bool:
        """
        Uploads a JSON-serializable object as a file to S3.
        :param data: JSON-serializable data.
        :param s3_key: S3 object key.
        :param extra_args: Extra arguments for upload (e.g., ContentType).
        :return: True if upload succeeded, False otherwise.
        """
        try:
            json_data = json.dumps(data)
            self.s3.put_object(Bucket=self.bucket_name, Key=s3_key, Body=json_data, ContentType='application/json', **(extra_args or {}))
            return True
        except ClientError as e:
            print(f"Failed to upload JSON to {s3_key}: {e}")
            return False

    def download_file(self, s3_key: str, file_path: str) -> bool:
        """
        Downloads a file from S3.
        :param s3_key: S3 object key.
        :param file_path: Local path to save the file.
        :return: True if download succeeded, False otherwise.
        """
        try:
            self.s3.download_file(self.bucket_name, s3_key, file_path)
            return True
        except ClientError as e:
            print(f"Failed to download {s3_key} to {file_path}: {e}")
            return False

    def get_file_content(self, s3_key: str) -> Optional[str]:
        """
        Retrieves the content of a file from S3 as bytes.
        :param s3_key: S3 object key.
        :return: File content as bytes, or None if failed.
        """
        try:
            response = self.s3.get_object(Bucket=self.bucket_name, Key=s3_key)
            bytes = response['Body'].read()
            text = bytes.decode('utf-8')
            return text
        except ClientError as e:
            print(f"Failed to get content of {s3_key}: {e}")
            return None
        
    def mock_get_file_content(self, file: str) -> Optional[str]:
        return Path(cfg.path.data.raw / "aws_doc_batch_1" / file).read_text()
    
    def get_json(self, s3_key: str) -> Optional[Any]:
        """
        Retrieves and parses a JSON file from S3.
        :param s3_key: S3 object key.
        :return: Parsed JSON object, or None if failed.
        """
        try:
            response = self.s3.get_object(Bucket=self.bucket_name, Key=s3_key)
            return json.loads(response['Body'].read().decode('utf-8'))
        except ClientError as e:
            print(f"Failed to get JSON from {s3_key}: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"Failed to decode JSON from {s3_key}: {e}")
            return None

    def list_files(self, prefix: str = "") -> List[str]:
        """
        Lists all files in the bucket with the given prefix.
        :param prefix: Prefix to filter files.
        :return: List of S3 object keys.
        """
        keys = []
        paginator = self.s3.get_paginator('list_objects_v2')
        try:
            for page in paginator.paginate(Bucket=self.bucket_name, Prefix=prefix):
                for obj in page.get('Contents', []):
                    keys.append(obj['Key'])
        except ClientError as e:
            print(f"Failed to list files with prefix '{prefix}': {e}")
        return keys
