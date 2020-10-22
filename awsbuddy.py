# Menue
from __future__ import print_function, unicode_literals
import subprocess
from PyInquirer import style_from_dict, Token, prompt, Separator
from pprint import pprint
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

try:
    account_id = sts.get_caller_identity()["Account"]
except Exception as ex:
    print('Error: Please set your credentials first.')
    exit()
# Check if budget exist
# yes
# do nothig
# no
# ask for budget
# display menu 100; 200; 500; 1000
# create budget
# check subscriber


def deployMonitoring():
    bashCommand = 'cd building_blocks/buckwatch/;npm run build;cdk deploy buckwatch-stack'
    process = subprocess.Popen(
        bashCommand, stdout=subprocess.PIPE, shell=True)
    output, error = process.communicate()

    print(output)
    print(error)


def destroyMonitoring():
    bashCommand = 'cd building_blocks/buckwatch/;npm run build;cdk destroy buckwatch-stack --force'
    process = subprocess.Popen(
        bashCommand, stdout=subprocess.PIPE, shell=True)
    output, error = process.communicate()

    print(output)
    print(error)


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
    _month = getCosts(
        '{}-01'.format(datetime.today().strftime("%Y-%m")),
        '{}'.format(datetime.today().strftime("%Y-%m-%d"))
    )
    _total = getCosts(
        '{}-01-01'.format(datetime.today().strftime("%Y")),
        '{}'.format(datetime.today().strftime("%Y-%m-%d"))
    )
    print('The ressources in {} for this month are {} USD and {} USD total this year.'.format(
        account_id, _month, _total))


def checkSecurityHub():
    try:
        response = client.describe_hub()
        secHubArn = (response["HubArn"])

        print("Security Hub is enabled! Yess")

    except client.exceptions.InvalidAccessException:
        print("Security Hub is not enabled... oO")


def enableSecuHub():
    enableSecHub()


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


def draw_budget():
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


def get_menu_options(answers):
    options = ['Budget', 'Costs', 'Security',
               'Deploy', 'Destroy', 'CreateBudget', 'DeleteBudget', 'About', 'Exit']
    return options


def draw_intro():
    print('\n\n\nAWS Buddy 2020 Version: {}'.format(version))
    print('Copyright ZERODOTFIVE UG')
    print('Please contribute: {}\n'.format(
        'https://github.com/ZDF-UG/awsbuddy'))


def deleteBudget(budgetName):
    try:
        print("ECreating Budget {} ....".format(budgetName))
        response = budget.delete_budget(
            AccountId=account_id,
            BudgetName=budgetName
        )
    except budget.exceptions.NotFoundException:
        print("Budget {} not found.".format(budgetName))


def createBudget(budget_name, budget_amount, notification_type, mail, threshold_percent):
    try:
        response = budget.create_budget(
            AccountId=account_id,
            Budget={
                'BudgetName': budget_name,
                'BudgetLimit': {
                    'Amount': budget_amount,
                    'Unit': 'USD'
                },
                'CostTypes': {
                    'IncludeTax': True,
                    'IncludeSubscription': True,
                    'UseBlended': True,
                    'IncludeRefund': True,
                    'IncludeCredit': True,
                    'IncludeUpfront': True,
                    'IncludeRecurring': True,
                    'IncludeOtherSubscription': True,
                    'IncludeSupport': True,
                    'IncludeDiscount': False,
                    'UseAmortized': False
                },
                'TimeUnit': 'MONTHLY',
                'BudgetType': 'COST'
            },
            NotificationsWithSubscribers=[
                {
                    'Notification': {
                        'NotificationType': notification_type,
                        'ComparisonOperator': 'GREATER_THAN',
                        'Threshold': threshold_percent,
                        'ThresholdType': 'PERCENTAGE'
                    },
                    'Subscribers': [
                        {
                            'SubscriptionType': 'EMAIL',
                            'Address': mail
                        },
                    ]
                },
            ]
        )
    except budget.exceptions.DuplicateRecordException:
        print("Budget {} does already exist.".format(budget_name))


def draw_main():

    questions = [

        {
            'type': 'list',
            'name': 'Option',
            'message': 'This is the main menu. Please choose one of the following actions:',
            'choices': get_menu_options,
            'validate': lambda answer: 'You must choose at least one Option.'
            if len(answer) == 0 else True
        },
    ]

    answers = prompt(questions, style=style)
    # pprint(answers)

    if answers['Option'] == 'Budget':
        checkBudget()
        draw_budget()
    if answers['Option'] == 'Costs':
        DisplayCosts()
    if answers['Option'] == 'DeleteBudget':
        deleteBudget("AWSBuddy_1")
        deleteBudget("AWSBuddy_2")

    if answers['Option'] == 'CreateBudget':
        createBudget("AWSBuddy_1", "100", 'FORECASTED', 'ayoub@umoru.de', 80)
        createBudget("AWSBuddy_2", "100", 'ACTUAL', 'ayoub@umoru.de', 80)

    if answers['Option'] == 'Security':
        checkSecurityHub()
    if answers['Option'] == 'Exit':
        return 0
    if answers['Option'] == 'About':
        draw_intro()
    if answers['Option'] == 'Deploy':
        deployMonitoring()
    if answers['Option'] == 'Destroy':
        destroyMonitoring()
    draw_main()


draw_intro()
draw_main()
