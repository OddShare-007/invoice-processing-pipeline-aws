"""AWS Lambda handler for extracting invoice data with Amazon Textract."""

import json
import logging
import os
from datetime import date, datetime
from decimal import Decimal
from typing import Any
from urllib.parse import unquote_plus

import boto3
from botocore.exceptions import BotoCoreError, ClientError


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

s3_client = boto3.client("s3")
textract_client = boto3.client("textract")
PROCESSED_BUCKET = os.environ.get(
    "PROCESSED_BUCKET", "shubh-invoices-processed"
)


def lambda_handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
    """Process S3 upload events and return a summary of processed records."""
    processed_records = []

    try:
        # Process every S3 record in the event so batched notifications are supported.
        for record in event.get("Records", []):
            source_bucket, source_key = _get_s3_object_location(record)
            logger.info(
                "Processing invoice: bucket=%s key=%s",
                source_bucket,
                source_key,
            )

            textract_response = _analyze_expense(source_bucket, source_key)
            invoice_data = _format_invoice_data(
                source_bucket,
                source_key,
                textract_response,
            )
            output_key = _build_output_key(source_key)
            _save_json(output_key, invoice_data)
            processed_records.append(output_key)

        return {
            "statusCode": 200,
            "processed": processed_records,
        }
    except (BotoCoreError, ClientError, KeyError, TypeError, ValueError):
        logger.exception("Invoice processing failed")
        raise


def _get_s3_object_location(record: dict[str, Any]) -> tuple[str, str]:
    """Extract and URL-decode the source bucket and object key from an S3 event."""
    try:
        bucket = record["s3"]["bucket"]["name"]
        encoded_key = record["s3"]["object"]["key"]
    except KeyError as error:
        raise ValueError("S3 event record is missing bucket or object key") from error

    return bucket, unquote_plus(encoded_key)


def _analyze_expense(bucket: str, key: str) -> dict[str, Any]:
    """Call Textract AnalyzeExpense for the uploaded S3 object."""
    logger.info("Calling Textract AnalyzeExpense for bucket=%s key=%s", bucket, key)
    return textract_client.analyze_expense(
        Document={"S3Object": {"Bucket": bucket, "Name": key}}
    )


def _format_invoice_data(
    source_bucket: str,
    source_key: str,
    textract_response: dict[str, Any],
) -> dict[str, Any]:
    """Convert the Textract response into a compact, query-friendly JSON object."""
    document = (textract_response.get("ExpenseDocuments") or [{}])[0]
    summary_fields = document.get("SummaryFields", [])

    summary_values = {
        "vendor_name": _get_summary_value(summary_fields, "VENDOR_NAME"),
        "invoice_date": _get_summary_value(summary_fields, "INVOICE_RECEIPT_DATE"),
        "total_amount": _get_summary_value(summary_fields, "TOTAL"),
        "tax_amount": _get_summary_value(summary_fields, "TOTAL_TAX"),
    }

    return {
        "source": {"bucket": source_bucket, "key": source_key},
        **summary_values,
        "line_items": _get_line_items(document.get("LineItemGroups", [])),
    }


def _get_summary_value(
    summary_fields: list[dict[str, Any]], field_type: str
) -> str | None:
    """Return the first normalized text value for a Textract summary field."""
    for field in summary_fields:
        if field.get("Type", {}).get("Text") == field_type:
            value = field.get("ValueDetection", {}).get("Text")
            if value is not None:
                return str(value)
    return None


def _get_line_items(line_item_groups: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Extract normalized line-item fields from Textract line-item groups."""
    line_items = []

    for group in line_item_groups:
        for line_item in group.get("LineItems", []):
            item = {}
            for field in line_item.get("LineItemExpenseFields", []):
                field_type = field.get("Type", {}).get("Text")
                value = field.get("ValueDetection", {}).get("Text")
                if field_type and value is not None:
                    item[_to_snake_case(field_type)] = str(value)
            if item:
                line_items.append(item)

    return line_items


def _to_snake_case(value: str) -> str:
    """Convert Textract field labels into stable JSON property names."""
    return value.lower().replace(" ", "_")


def _build_output_key(source_key: str) -> str:
    """Replace the source file extension with .json while preserving its key path."""
    filename, extension = os.path.splitext(source_key)
    return f"{filename}.json" if extension else f"{source_key}.json"


def _save_json(output_key: str, invoice_data: dict[str, Any]) -> None:
    """Serialize the invoice record and save it to the processed S3 bucket."""
    body = json.dumps(invoice_data, default=_json_serializer, indent=2)
    logger.info("Saving processed invoice: bucket=%s key=%s", PROCESSED_BUCKET, output_key)
    s3_client.put_object(
        Bucket=PROCESSED_BUCKET,
        Key=output_key,
        Body=body.encode("utf-8"),
        ContentType="application/json",
    )


def _json_serializer(value: Any) -> str:
    """Serialize common AWS/Python date and numeric values if they occur in output."""
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, Decimal):
        return str(value)
    raise TypeError(f"Object of type {type(value).__name__} is not JSON serializable")
