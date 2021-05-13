#!/usr/bin/env python3
"""
API code for displaying generic message or echoing a custom message
"""
import json
import logging

logging.basicConfig(level=logging.INFO)


def lambda_handler(event, context):
    # pylint: disable=unused-argument
    """
    Simple hello world example
    """
    logging.info("Received : %s", json.dumps(event))
    return {"statusCode": 200, "body": "Hello world!"}
