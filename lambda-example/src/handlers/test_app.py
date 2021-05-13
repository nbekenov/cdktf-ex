import logging

import app


def test_lambda_handler(caplog):
    caplog.set_level(logging.INFO)
    response = app.lambda_handler({"beer": 1}, None)
    assert response == {"body": "Hello world!", "statusCode": 200}
    assert 'Received : {"beer": 1}' in caplog.text
