output "raw_bucket_name" {
  value = aws_s3_bucket.raw.id
}

output "processed_bucket_name" {
  value = aws_s3_bucket.processed.id
}

output "lambda_function_name" {
  value = aws_lambda_function.invoice_processor.function_name
}