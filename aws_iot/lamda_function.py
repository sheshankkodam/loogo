'''
This is a sample Lambda function that sends an SMS on click of a
button. It needs one permission sns:Publish. The following policy
allows SNS publish to SMS but not topics or endpoints.
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "sns:Publish"
            ],
            "Resource": [
                "*"
            ]
        },
        {
            "Effect": "Deny",
            "Action": [
                "sns:Publish"
            ],
            "Resource": [
                "arn:aws:sns:*:*:*"
            ]
        }
    ]
}

The following JSON template shows what is sent as the payload:
{
    "serialNumber": "GXXXXXXXXXXXXXXXXX",
    "batteryVoltage": "xxmV",
    "clickType": "SINGLE" | "DOUBLE" | "LONG"
}

A "LONG" clickType is sent if the first press lasts longer than 1.5 seconds.
"SINGLE" and "DOUBLE" clickType payloads are sent for short clicks.

For more documentation, follow the link below.
http://docs.aws.amazon.com/iot/latest/developerguide/iot-lambda-rule.html
'''

from __future__ import print_function

import boto3
import json
import logging
import requests

logger = logging.getLogger()
logger.setLevel(logging.INFO)

sns = boto3.client('sns')
phone_numbers = ['1-617-750-4465', '1-850-291-3447']
washroom = '90SecondNorth'


def send_sms(message):
    for phone_number in phone_numbers:
        sns.publish(PhoneNumber=phone_number, Message=message)
        logger.info('SMS has been sent to ' + phone_number)


def lambda_handler(event, context):
    logger.info('Received event: ' + json.dumps(event))
    click_type = event.get('clickType')
    if click_type == "SINGLE":
        message = '%s is closed for cleaning' % washroom
        send_sms(message)
        requests.post('https://hooks.slack.com/services/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',json={"text": message})
        requests.put('http://34.208.93.80:5002/washrooms/90SecondNorth', json={"status": "closed for cleaning"})
        requests.put('http://34.208.93.80:5002/echopath/washrooms/90SecondNorth', json={"status": "closed for cleaning"})
    elif click_type == "DOUBLE":
        message = '%s is active' % washroom
        send_sms(message)
        requests.post('https://hooks.slack.com/services/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',json={"text": message})
        requests.put('http://34.208.93.80:5002/washrooms/90SecondNorth', json={"status": "active"})
        requests.put('http://34.208.93.80:5002/echopath/washrooms/90SecondNorth', json={"status": "active"})
    elif click_type == "LONG":
        message = '%s is under service' % washroom
        send_sms(message)
        requests.post('https://hooks.slack.com/services/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', json={"text": message})
        requests.put('http://34.208.93.80:5002/washrooms/90SecondNorth', json={"status": "in service"})
        requests.put('http://34.208.93.80:5002/echopath/washrooms/90SecondNorth', json={"status": "in service"})
    else:
        pass
