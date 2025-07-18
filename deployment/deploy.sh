#!/bin/bash

set -e

# --- Configuration ---
# You can pre-fill these variables or the script will prompt you.
AWS_REGION="us-east-1"
FUNCTION_NAME="s3-unzip-function"
ROLE_NAME="S3UnzipLambdaRole"
POLICY_NAME="S3UnzipPolicy"
HANDLER_FILE="s3_handler.py"
LAMBDA_ZIP_FILE="s3_unzip_handler.zip"

# --- Script ---

# 1. Get User Input
read -p "Enter your S3 bucket name: " BUCKET_NAME
read -p "Enter your AWS Account ID: " AWS_ACCOUNT_ID

# 2. Define ARNs and Paths
ROLE_ARN="arn:aws:iam::${AWS_ACCOUNT_ID}:role/${ROLE_NAME}"
LAMBDA_ARN_BASE="arn:aws:lambda:${AWS_REGION}:${AWS_ACCOUNT_ID}:function:${FUNCTION_NAME}"
BUILD_DIR="build"
TEMPLATE_DIR="templates"
SRC_DIR="../handlers"

# 3. Create Build Directory
echo "--- Creating build directory ---"
mkdir -p "${BUILD_DIR}"

# 4. Package Lambda Function
echo "--- Packaging Lambda function ---"
cp "${SRC_DIR}/${HANDLER_FILE}" "${BUILD_DIR}/"
(cd "${BUILD_DIR}" && zip "${LAMBDA_ZIP_FILE}" "${HANDLER_FILE}")

# 5. Process Policy Templates
echo "--- Processing policy templates ---"
sed "s/<YOUR_BUCKET_NAME>/${BUCKET_NAME}/g" "${TEMPLATE_DIR}/s3-policy.json" > "${BUILD_DIR}/s3-policy.json"
sed "s|<YOUR_LAMBDA_FUNCTION_ARN>|${LAMBDA_ARN_BASE}|g" "${TEMPLATE_DIR}/notification.json" > "${BUILD_DIR}/notification.json"

# 6. Create IAM Role and Attach Policies
echo "--- Creating IAM Role and attaching policies ---"
aws iam create-role \
  --role-name "${ROLE_NAME}" \
  --assume-role-policy-document "file://${TEMPLATE_DIR}/lambda-trust-policy.json" \
  --output text --query 'Role.Arn'

aws iam attach-role-policy \
  --role-name "${ROLE_NAME}" \
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole

aws iam put-role-policy \
  --role-name "${ROLE_NAME}" \
  --policy-name "${POLICY_NAME}" \
  --policy-document "file://${BUILD_DIR}/s3-policy.json"

echo "Waiting for IAM role to propagate..."
sleep 10

# 7. Create Lambda Function
echo "--- Creating Lambda function ---"
aws lambda create-function \
  --function-name "${FUNCTION_NAME}" \
  --zip-file "fileb://${BUILD_DIR}/${LAMBDA_ZIP_FILE}" \
  --handler "${HANDLER_FILE%.py}.lambda_handler" \
  --runtime python3.11 \
  --role "${ROLE_ARN}" \
  --region "${AWS_REGION}" \
  --output text --query 'FunctionArn'

# 8. Add S3 Trigger
echo "--- Adding S3 trigger ---"
aws lambda add-permission \
  --function-name "${FUNCTION_NAME}" \
  --action "lambda:InvokeFunction" \
  --principal s3.amazonaws.com \
  --source-arn "arn:aws:s3:::${BUCKET_NAME}" \
  --source-account "${AWS_ACCOUNT_ID}" \
  --region "${AWS_REGION}"

aws s3api put-bucket-notification-configuration \
  --bucket "${BUCKET_NAME}" \
  --notification-configuration "file://${BUILD_DIR}/notification.json" \
  --region "${AWS_REGION}"

# 9. Cleanup
echo "--- Cleaning up build files ---"
rm -rf "${BUILD_DIR}"

echo "--- Deployment successful! ---"
