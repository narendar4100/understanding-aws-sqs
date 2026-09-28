"""Core Banking Ledger consumer.

Architecture A invokes this function synchronously through API Gateway.
Architecture B invokes the same code from an SQS event source mapping.
Both paths simulate one ACID ledger commit with a fixed 1.5 second critical
section so students can see the difference between a throttled synchronous
write and a durable queue accept.
"""

import base64
import json
import logging
import os
import time

logger = logging.getLogger()
logger.setLevel(logging.INFO)

LEDGER_MODE = os.environ.get("LEDGER_MODE", "UNSPECIFIED")

CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type",
    "Access-Control-Allow-Methods": "OPTIONS,POST",
    "Content-Type": "application/json",
}


def _parse_json(raw):
    if raw is None or raw == "":
        return {}
    if isinstance(raw, dict):
        return raw
    if not isinstance(raw, str):
        return {"raw": str(raw)}
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        logger.warning("Ledger payload was not valid JSON")
        return {"raw": raw}
    if isinstance(parsed, dict):
        return parsed
    return {"raw": parsed}


def _decode_http_body(event):
    raw_body = event.get("body")
    if raw_body and event.get("isBase64Encoded"):
        raw_body = base64.b64decode(raw_body).decode("utf-8")
    return _parse_json(raw_body)


def _queue_kind(record):
    source_arn = record.get("eventSourceARN", "")
    if source_arn.endswith(".fifo"):
        return "FIFO"
    if source_arn:
        return "STANDARD"
    return "DIRECT"


def _commit_ledger_entry(entry, request_id, queue_kind="DIRECT", message_id="-"):
    """Simulate an enterprise ledger write and its ACID critical section.

    BEGIN pins the account row, the sleep stands in for the journal flush
    and commit, and COMMIT is logged only after that critical section ends.
    There is no real database behind this training function.
    """
    account_id = entry.get("accountId", "UNKNOWN")
    amount = entry.get("amount", 0)
    sequence = entry.get("seq", "-")
    transfer_id = entry.get("transferId", "-")
    description = entry.get("description", "-")
    logger.info(
        "BEGIN ledger transaction mode=%s queue=%s seq=%s transfer_id=%s message_id=%s account=%s amount=%s description=%s",
        LEDGER_MODE,
        queue_kind,
        sequence,
        transfer_id,
        message_id,
        account_id,
        amount,
        description,
    )
    time.sleep(1.5)
    logger.info(
        "COMMIT ledger transaction mode=%s queue=%s seq=%s transfer_id=%s message_id=%s account=%s amount=%s description=%s",
        LEDGER_MODE,
        queue_kind,
        sequence,
        transfer_id,
        message_id,
        account_id,
        amount,
        description,
    )
    return {
        "status": "COMMITTED",
        "mode": LEDGER_MODE,
        "queue": queue_kind,
        "seq": sequence,
        "transferId": transfer_id,
        "accountId": account_id,
        "amount": amount,
        "requestId": request_id,
    }


def _http_response(status_code, payload):
    return {
        "statusCode": status_code,
        "headers": CORS_HEADERS,
        "body": json.dumps(payload),
    }


def handler(event, context):
    request_id = getattr(context, "aws_request_id", "local")
    records = event.get("Records") if isinstance(event, dict) else None

    if isinstance(records, list):
        committed = []
        for record in records:
            payload = _parse_json(record.get("body"))
            committed.append(
                _commit_ledger_entry(
                    payload,
                    request_id,
                    _queue_kind(record),
                    record.get("messageId", "-"),
                )
            )
        return _http_response(200, {"committed": committed})

    method = (
        event.get("requestContext", {})
        .get("http", {})
        .get("method", "")
        .upper()
    )
    if method == "OPTIONS":
        return _http_response(200, {"status": "OK"})

    committed = _commit_ledger_entry(_decode_http_body(event), request_id)
    return _http_response(200, committed)
