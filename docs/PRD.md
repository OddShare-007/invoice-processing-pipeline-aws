# Product Requirements Document

## Problem Statement
Small businesses often enter invoice and receipt data manually, which is slow, repetitive, and prone to transcription errors. This project automates document intake and expense extraction so structured records are available for downstream reporting and review.

## Target Users
Small-business owners, bookkeepers, and operations staff who currently enter invoice or receipt details manually and need a simple, low-maintenance workflow.

## Core Features
- Accept invoice and receipt files in an Amazon S3 raw bucket.
- Automatically trigger processing when a document is uploaded.
- Use AWS Textract AnalyzeExpense to extract vendor, totals, dates, line items, and related expense fields.
- Normalize extracted data into consistent JSON records.
- Store processed records in a separate S3 bucket for analysis.
- Support querying processed records with Amazon Athena.
- Log processing activity and failures for operational review.

## Success Criteria
- A valid uploaded document is processed automatically without manual intervention.
- Extracted records are valid JSON and retain the key fields returned by Textract.
- Processed output is stored separately from raw documents and is queryable in Athena.
- Failures are logged with enough context to diagnose the document and processing step.
- The pipeline reduces manual invoice-entry effort and provides a repeatable foundation for future integrations.
