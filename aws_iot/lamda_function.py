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
phone_numbers = ['1-617-750-4465']
hipchat = "https://changeagents.hipchat.com/v2/room/4036142/notification?auth_token=7ShqgwAsYQ2hJoRgwcg7FagyiHONP8gnMZep326W"
slack = 'https://hooks.slack.com/services/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'
loogoUrl = 'http://52.25.29.73:5002/washrooms/'
echoPathUrl = 'http://52.25.29.73:5002/echopath/washrooms/'
loogoameegoUrl = 'http://loogoameego.ssedev.io/restroom'
washrooms = {'G030MD037206HRE4': "RushHour2Mens", 'G030MD0232733SN8': "RushHour2Womens",
             "G030MD039197T47D": "FinalDestination2Mens", "G030MD037225H5WR": "FinalDestination2Womens"}


def handle_notifications(status_msg, battery_voltage, serial_no, color):
    notification_msg = washrooms.get(serial_no) + " is " + status_msg
    # sms
    for phone_number in phone_numbers:
        sns.publish(PhoneNumber=phone_number, Message=notification_msg)
        logger.info('SMS has been sent to ' + phone_number)

    # hipchat and slack
    requests.post(hipchat, {"color": color, "notify": "true", "message": notification_msg})
    requests.post(slack, json={"text": notification_msg})

    # echopath
    # requests.put(echoPathUrl + washroom, json={"status": "closed for cleaning"})

    # save in db
    requests.put(loogoUrl + washrooms.get(serial_no), json={"aws_sno": serial_no, "battery_voltage": battery_voltage,
                                                            "status": status_msg})

    # Update Loogoameego
    requests.put(loogoameegoUrl, json={"restroomname": washrooms.get(serial_no), "status": status_msg})


def lambda_handler(event, context):
    logger.info('Received event: ' + json.dumps(event))
    click_type = event.get('clickType')
    serial_no = event.get('serialNumber')
    battery_voltage = event.get('batteryVoltage')
    if click_type == "SINGLE":
        status_msg = "closed for cleaning"
        handle_notifications(status_msg, battery_voltage, serial_no, "red")
    elif click_type == "DOUBLE":
        status_msg = "active"
        handle_notifications(status_msg, battery_voltage, serial_no, "green")
    elif click_type == "LONG":
        status_msg = "under service"
        handle_notifications(status_msg, battery_voltage, serial_no, "red")
    else:
        pass