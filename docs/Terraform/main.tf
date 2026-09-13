terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# S3 bucket for raw invoices
resource "aws_s3_bucket" "raw" {
  bucket = var.raw_bucket_name
}

# S3 bucket for processed invoices
resource "aws_s3_bucket" "processed" {
  bucket = var.processed_bucket_name
}

# IAM role for Lambda
resource "aws_iam_role" "lambda_role" {
  name = "invoice-processor-role-tf"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "lambda.amazonaws.com"
      }
    }]
  })
}

# IAM policy for Lambda permissions
resource "aws_iam_role_policy" "lambda_policy" {
  name = "invoice-processor-policy-tf"
  role = aws_iam_role.lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = ["s3:GetObject"]
        Resource = "${aws_s3_bucket.raw.arn}/*"
      },
      {
        Effect = "Allow"
        Action = ["s3:PutObject"]
        Resource = "${aws_s3_bucket.processed.arn}/*"
      },
      {
        Effect = "Allow"
        Action = ["textract:AnalyzeExpense"]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = ["logs:CreateLogGroup", "logs:CreateLogStream", "logs:PutLogEvents"]
        Resource = "arn:aws:logs:*:*:*"
      }
    ]
  })
}

# Lambda function
resource "aws_lambda_function" "invoice_processor" {
  function_name = "invoice-processor-tf"
  role          = aws_iam_role.lambda_role.arn
  handler       = "lambda_function.lambda_handler"
  runtime       = "python3.12"
  timeout       = 30
  filename      = "${path.module}/lambda_function.zip"

  environment {
    variables = {
      PROCESSED_BUCKET = var.processed_bucket_name
    }
  }
}

# Permission for S3 to invoke Lambda
resource "aws_lambda_permission" "allow_s3" {
  statement_id  = "AllowS3Invoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.invoice_processor.function_name
  principal     = "s3.amazonaws.com"
  source_arn    = aws_s3_bucket.raw.arn
}

# S3 trigger
resource "aws_s3_bucket_notification" "raw_bucket_trigger" {
  bucket = aws_s3_bucket.raw.id

  lambda_function {
    lambda_function_arn = aws_lambda_function.invoice_processor.arn
    events              = ["s3:ObjectCreated:*"]
  }

  depends_on = [aws_lambda_permission.allow_s3]
}