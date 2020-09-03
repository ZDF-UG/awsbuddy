# Menue
from __future__ import print_function, unicode_literals

from pprint import pprint

from PyInquirer import prompt, Separator

from examples import custom_style_2
# end
import boto3
import argparse
import configparser
import os
import botocore.exceptions
from datetime import datetime

version = "Gin"
client = boto3.client('securityhub')
costs = boto3.client('ce')
budget = boto3.client('budgets')
sts = boto3.client('sts')
# SecurityHub
awsbuddy_budget = "AWSBuddy_Default"
account_id = sts.get_caller_identity()["Account"]
# Check if budget exist
# yes
# do nothig
# no
# ask for budget
# display menu 100; 200; 500; 1000
# create budget
# check subscriber


def checkBudget():

    try:
        print("Checking budget ....")
        response = budget.describe_budget(
            AccountId=account_id,
            BudgetName=awsbuddy_budget
        )
    except budget.exceptions.NotFoundException:
        print("Budget not setup... ")


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
checkBudget()
DisplayCosts()
try:
    response = client.describe_hub()
    secHubArn = (response["HubArn"])
    secHubCheckResult(True)
except client.exceptions.InvalidAccessException:
    secHubCheckResult(False)
    enableSecHub()

style = style_from_dict({
    Token.Separator: '#cc5454',
    Token.QuestionMark: '#673ab7 bold',
    Token.Selected: '#cc5454',  # default
    Token.Pointer: '#673ab7 bold',
    Token.Instruction: '',  # default
    Token.Answer: '#f44336 bold',
    Token.Question: '',
})


def get_budget_options(answers):
    options = ['50', '100', '200', '300']
    return options


questions = [

    {
        'type': 'list',
        'name': 'Budget',
        'message': 'Budget Setup',
        'choices': get_budget_options,
        'validate': lambda answer: 'You must choose at least one Budget.'
        if len(answer) == 0 else True
    },
    {
        'type': 'list',
        'message': 'Select Notification Option',
        'name': 'Notification',
        'choices': [
            {
                'name': 'yes'
            },
            {
                'name': 'no'
            },

        ],
        'validate': lambda answer: 'You must choose at least one Budget.'
        if len(answer) == 0 else True
    },
]

answers = prompt(questions, style=style)
pprint(answers)
