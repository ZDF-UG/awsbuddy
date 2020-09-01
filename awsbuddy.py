
import boto3
import argparse
import configparser
import os
import botocore.exceptions
from datetime import datetime

version = "Gin"
client = boto3.client('securityhub')
costs = boto3.client('ce')
# SecurityHub


def getCosts(start, end):
    response = costs.get_cost_and_usage(
        TimePeriod={
            'Start': start,
            'End': end
        },
        Granularity='MONTHLY',
        Metrics=[
            "BlendedCost", "UnblendedCost", "UsageQuantity",
        ]
    )
    total = 0
    for month in response['ResultsByTime']:
        monthTotal = round(float(month['Total']['BlendedCost']['Amount']), 0)
        total += monthTotal

    return (total)


def DisplayCosts():
    print('Current month costs: {}'.format(
        getCosts(
            '{}-01'.format(datetime.today().strftime("%Y-%m")),
            '{}'.format(datetime.today().strftime("%Y-%m-%d"))
        ))
    )

    print('Current total costs: {}'.format(
        getCosts(
            '{}-01-01'.format(datetime.today().strftime("%Y")),
            '{}'.format(datetime.today().strftime("%Y-%m-%d"))
        ))
    )


def secHubCheckResult(enabled):
    if enabled == True:
        print("Security Hub is enabled! Yess")
    else:
        print("Security Hub is not enabled... oO")


def enableSecHub():
    try:
        print("Enabling SecurityHub ....")
        response = client.enable_security_hub(
            Tags={
                'AWSBuddy': version
            },
            EnableDefaultStandards=False
        )
    except client.exceptions.AccessDeniedException:
        print("Cannot enable SecurityHub - check your permissions... ")


Config = configparser.ConfigParser()
Config.read(os.path.expanduser('~/.aws/credentials'))

sections = Config.sections()
# for profile in sections:
# print(profile)

DisplayCosts()
try:
    response = client.describe_hub()
    secHubArn = (response["HubArn"])
    secHubCheckResult(True)
except client.exceptions.InvalidAccessException:
    secHubCheckResult(False)
    enableSecHub()
