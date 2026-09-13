# Build Phases

## Phase 1 - S3 Bucket Setup
Create separate raw and processed S3 buckets with clear object-key conventions, encryption, access controls, and an initial upload workflow.

## Phase 2 - Lambda + Textract Integration
Implement the Python 3.12 Lambda handler, connect S3 events to Lambda, call Textract `AnalyzeExpense`, transform the response, and write processed JSON output.

## Phase 3 - Athena Querying
Define the processed-data layout and Athena schema, then add representative SQL queries for vendors, totals, dates, and processing results.

## Phase 4 - Error Handling and Monitoring
Add validation, retries where appropriate, structured logging, CloudWatch metrics, and a clear failure path for invalid documents or service errors.

## Phase 5 - Terraform + CI/CD
Define AWS resources as Terraform, add environment-specific configuration, and configure CI checks for tests, formatting, validation, and deployment workflows.

## Phase 6 - Documentation and Demo
Complete the README and architecture documentation, add diagrams and example queries, and prepare a short end-to-end demonstration from upload through Athena results.
