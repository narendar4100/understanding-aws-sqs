"""Checkout fan-out for the SNS training lab.

The static site calls place() through API Gateway. That function decides the
business facts, then publishes one message. Each subscriber's filter policy
decides whether the message is delivered. The workers only log the hand-off;
there is no payment or warehouse system behind them.
"""

import json
import logging
import os
import re
import uuid

logger = logging.getLogger()
logger.setLevel(logging.INFO)

TOPIC_ARN = os.environ.get("TOPIC_ARN", "")
SES_FROM_EMAIL = os.environ.get("SES_FROM_EMAIL", "")
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def decide(order):
    """Turn a checkout into SNS attributes and the subscribers that match."""
    item_type = str(order.get("itemType", "")).strip().lower()
    payment = str(order.get("payment", "")).strip().lower()
    bill = str(order.get("billCountry", "")).strip().upper()
    ship = str(order.get("shipCountry", "")).strip().upper()
    email = str(order.get("customerEmail", "")).strip()
    amount = order.get("amount", 0)

    if item_type not in ("physical", "digital"):
        raise ValueError("itemType must be physical or digital")
    if payment not in ("approved", "declined"):
        raise ValueError("payment must be approved or declined")
    if len(bill) != 2 or len(ship) != 2 or not bill.isalpha() or not ship.isalpha():
        raise ValueError("billCountry and shipCountry must be two letters")
    if email and not EMAIL_RE.match(email):
        raise ValueError("customerEmail must be empty or a single email address")
    try:
        amount = round(float(amount), 2)
    except (TypeError, ValueError):
        raise ValueError("amount must be a number")
    if amount < 0:
        raise ValueError("amount cannot be negative")

    risk = "review" if bill != ship else "clear"
    has_email = "true" if email else "false"
    if has_email == "false":
        ops_route = "missing-email"
    elif payment == "declined" or risk == "review":
        ops_route = "urgent"
    else:
        ops_route = "none"

    message = {
        "orderId": str(order.get("orderId") or uuid.uuid4()),
        "eventType": "OrderPlaced",
        "itemType": item_type,
        "payment": payment,
        "amount": amount,
        "billCountry": bill,
        "shipCountry": ship,
        "customerEmail": email,
        "risk": risk,
        "hasCustomerEmail": has_email,
        "opsRoute": ops_route,
    }
    attributes = {
        "eventType": "OrderPlaced",
        "itemType": item_type,
        "payment": payment,
        "risk": risk,
        "hasCustomerEmail": has_email,
        "opsRoute": ops_route,
    }
    routes = [
        {
            "subscriber": "Billing queue",
            "matched": payment == "approved",
            "why": "payment = approved",
        },
        {
            "subscriber": "Shipping queue",
            "matched": payment == "approved" and item_type == "physical" and risk == "clear",
            "why": "payment = approved, itemType = physical, and risk = clear",
        },
        {
            "subscriber": "Risk Lambda",
            "matched": risk == "review",
            "why": "risk = review because the shipping country differs from the billing country",
        },
        {
            "subscriber": "Customer email Lambda",
            "matched": payment == "approved" and has_email == "true" and risk == "clear",
            "why": "payment = approved, a customer email exists, and risk = clear",
        },
        {
            "subscriber": "Operations email",
            "matched": ops_route in ("missing-email", "urgent"),
            "why": "opsRoute = " + ops_route,
        },
    ]
    return message, attributes, routes


def _http(status, payload):
    return {
        "statusCode": status,
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Allow-Methods": "OPTIONS,POST",
            "Content-Type": "application/json",
        },
        "body": json.dumps(payload),
    }


def _body(event):
    raw = event.get("body")
    if raw and event.get("isBase64Encoded"):
        import base64

        raw = base64.b64decode(raw).decode("utf-8")
    if not raw:
        return {}
    parsed = json.loads(raw)
    if not isinstance(parsed, dict):
        raise ValueError("order body must be a JSON object")
    return parsed


def place(event, context):
    method = event.get("requestContext", {}).get("http", {}).get("method", "").upper()
    if method == "OPTIONS":
        return _http(200, {"status": "OK"})
    try:
        message, attributes, routes = decide(_body(event))
    except (ValueError, json.JSONDecodeError) as error:
        return _http(400, {"error": str(error)})
    if not TOPIC_ARN:
        return _http(500, {"error": "TOPIC_ARN is not configured"})

    import boto3

    response = boto3.client("sns").publish(
        TopicArn=TOPIC_ARN,
        Message=json.dumps(message),
        MessageAttributes={
            name: {"DataType": "String", "StringValue": value}
            for name, value in attributes.items()
        },
    )
    logger.info("Published order %s as SNS message %s", message["orderId"], response["MessageId"])
    return _http(200, {
        "orderId": message["orderId"],
        "messageId": response["MessageId"],
        "attributes": attributes,
        "routes": routes,
    })


def _sns_messages(event):
    messages = []
    for record in event.get("Records", []):
        sns = record.get("Sns", {})
        messages.append(json.loads(sns.get("Message", "{}")))
    return messages


def _sqs_messages(event):
    messages = []
    for record in event.get("Records", []):
        messages.append(json.loads(record.get("body", "{}")))
    return messages


def billing(event, context):
    for message in _sqs_messages(event):
        logger.info(
            "BILLING recorded order %s amount=%s payment=%s",
            message.get("orderId"),
            message.get("amount"),
            message.get("payment"),
        )
    return {"processed": len(event.get("Records", []))}


def shipping(event, context):
    for message in _sqs_messages(event):
        logger.info(
            "SHIPPING packed physical order %s for %s",
            message.get("orderId"),
            message.get("shipCountry"),
        )
    return {"processed": len(event.get("Records", []))}


def risk(event, context):
    for message in _sns_messages(event):
        logger.info(
            "REVIEW hold order %s: bill country %s, ship country %s",
            message.get("orderId"),
            message.get("billCountry"),
            message.get("shipCountry"),
        )
    return {"processed": len(event.get("Records", []))}


def customer(event, context):
    import boto3

    ses = boto3.client("ses")
    for message in _sns_messages(event):
        address = message.get("customerEmail", "")
        order_id = message.get("orderId", "")
        if not SES_FROM_EMAIL:
            logger.info("CUSTOMER email skipped for order %s; SES from address is not configured", order_id)
            continue
        try:
            ses.send_email(
                Source=SES_FROM_EMAIL,
                Destination={"ToAddresses": [address]},
                Message={
                    "Subject": {"Data": "Order " + order_id + " confirmed"},
                    "Body": {
                        "Text": {
                            "Data": "Your " + message.get("itemType", "item") + " order " + order_id + " is confirmed."
                        }
                    },
                },
            )
            logger.info("CUSTOMER email sent for order %s", order_id)
        except Exception:
            logger.exception("CUSTOMER email was not sent for order %s", order_id)
    return {"processed": len(event.get("Records", []))}
