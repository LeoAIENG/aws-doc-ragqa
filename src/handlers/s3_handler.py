import boto3
import zipfile
import io
import os

s3 = boto3.client("s3")


def lambda_handler(event, context):
    # Get the bucket and key (file name) from the S3 event
    for record in event["Records"]:
        bucket = record["s3"]["bucket"]["name"]
        key = record["s3"]["object"]["key"]

        # Check if the uploaded file is a zip file
        if key.endswith(".zip"):
            try:
                # Download the zip file to a buffer
                zip_object = s3.get_object(Bucket=bucket, Key=key)
                buffer = io.BytesIO(zip_object["Body"].read())

                # Unzip the file
                with zipfile.ZipFile(buffer, "r") as zip_file:
                    for file in zip_file.namelist():
                        # Extract the file to a buffer
                        extracted_file = zip_file.read(file)

                        # Construct the output path (e.g., preserving directory structure)
                        output_path = os.path.join(os.path.dirname(key), file)

                        # Upload the extracted file to S3
                        s3.put_object(
                            Bucket=bucket, Key=output_path, Body=extracted_file
                        )

                # Optionally, delete the original zip file
                # s3.delete_object(Bucket=bucket, Key=key)
            except Exception as e:
                print(e)
                raise e

    return {"statusCode": 200, "body": "Zip file processed successfully"}
