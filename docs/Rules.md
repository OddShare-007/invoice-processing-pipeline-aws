# Coding Rules

These rules apply to AI coding assistants and contributors working on this AWS Lambda project.

1. Use **Python 3.12** for runtime code and tests.
2. Use **boto3** for AWS service integration. Do not add third-party libraries unless they are clearly necessary and approved.
3. Include appropriate error handling around S3, Textract, serialization, and other external-service operations.
4. Add structured, useful logging with `logging`; do not log document contents, credentials, or sensitive data.
5. Never hardcode AWS credentials, secrets, tokens, bucket names tied to private environments, or other sensitive configuration in source code. Use IAM roles, environment variables, or managed configuration.
6. Follow AWS least-privilege IAM principles. Grant each role only the actions and resources it requires.
7. Keep functions small, modular, and testable. Separate event handling, Textract calls, transformation, and storage where practical.
8. Preserve idempotent behavior where possible so retries do not create confusing duplicate output.
9. Validate inputs and handle malformed events or unsupported documents explicitly.
10. Keep changes focused, document meaningful architectural decisions, and add or update tests for behavioral changes.
