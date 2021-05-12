#!/usr/bin/env python3
"""
API code for displaying generic message or echoing a custom message
"""
import datetime
import json
import os
import logging
import botocore
import boto3

# logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    # pylint: disable=unused-argument
    """
    Simple hellow world example
    """
    logger.info(f"Received : {json.dumps(event)}")
    return {"statusCode": 200, "body": "Hello world!"}