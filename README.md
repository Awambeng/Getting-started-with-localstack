# Getting-started-with-localstack.

## Introduction
Localstack is a platform for local development and testing of cloud applications. Localstack is a fully functional local AWS cloud stack that allows us to run, test our serverless applications locally without interacting with the actual AWS services. This makes it easier to develop, test and deploy our AWS-based applications.

A serverless application is an application that runs in the cloud and whose server infrastructure is managed by the cloud provider. So when you deploy a serverless application the cloud provider manages the server infrastructure of that application, automatically scales the resources and charges the user based on the actual usage.

Localstack runs in a single docker container on your laptop. Let's delve into the prerequisites for getting started with localstack.

## Prerequisites
- Docker
- Python (version 3.7 to 3.11 is supported)
- pip (Python package manager)

## Installation
1. Install docker on your machine. You can download and install it from the official website based on your operating system type.
 [download and install docker](https://www.docker.com/get-started)

 2. Install Localstack. You can follow the installation guide below to setup Localstack in your machine.
 [A guide to installing Localstack](https://docs.localstack.cloud/getting-started/installation/)

## Running Localstack
1. Start the Localstack environment by running the following command:
```bash
localstack start -d
```

## Practice guide
The aim of this section is to show ow we can deploy a serverless image resizer application that utilises AWS services. So here we will learn how to use localstack for development and testing of your AWS applications locally. This section walks you out in the key concepts below:

1. Starting a LocalStack instance on your local machine.
2. Deploy an aws serverless application locally.
3. Running an automated integration test suite against local infrastructure.
4. Exploring localstack web application to view deployed resources.
5. Destroying the local infrastructure you have provisioned.

## Instructions
To get started, clone the sample application (serverless image resizer) repository from GitHub.
```bash
git clone https://github.com/localstack-samples/sample-serverless-image-resizer-s3-lambda.git
cd sample-serverless-image-resizer-s3-lambda
```

After cloning and moving into the project directory you can now follow the steps or instructions to start localstack, deploy our sample application and test the application.

## Setup a virtual environment.
To be able to deploy the application you need to have specific python packages installed. To perform this step it is advisable t use virtual environment. Use the following commands to setup a virtual environment.
```python
python3 -m venv venv
source venv/bin/activate
pip install requirements-dev.txt
```

## Setup serverless image resizer.
This application enables severless image resizing using S3, SSM, Lambda, SNS, and SES. Below are short explanations of the services used in this application.

1. S3 (Simple Storage Service): It allows us to store and retrieve any amount of data at ay time from anywhere from the web. It is commonly used for storage, content distribution, backup and more.

2. SSM (AWS Systems Manager): This service helps us to automate and manage aws resources.

3. AWS Lambda: It is a serverless computing service that runs your code in response to events or requests. It automatically scales your application by running the code in response to each trigger, without the need to provision or manage servers.

4. SNS (Simple Notification Service): It is a messaging service that makes it easy to decouple and scale microservices, distributed systems and serverless applications. It allows us to send notifications to email addresses, SMS text messages, AWS Lambda functions and more.

5. SES (Simple Email Service): It is a cost-effective service that provides easy access to tools and infrastructure needed for high-quality email sending. It allows us to send transactional emails, such as order confirmations, and password resets, as well as marketing emails such as newsletters. It also provides feaures like delivery tracking and spam filtering.

The serverless image resizer allows users to upload and view resized images. The Lambda function generates S3 pre-signed URLs to upload the images while the S3 bucket notification trigger images resizing. In the project we have another lambda function that lists and provides pre-signed URLs for the browser to display. 

Our application handles lambda failures through SNS (Simple Notification Service) and SES (Simple Email Service).

The application uses the AWS CLI and the awslocal wrapper to deploy the application to LocalStack. 

In this guide we see how to deploy the application on LocalStack manually and automatically using a script.

## Manual Deployment.
1. Step 1: Create an S3 Bucket.
```bash
awslocal s3 mb s3://localstack-thumbnails-app-images
awslocal s3 mb s3://localstack-thumbnails-app-resized
```

After creating our buckets the next thing to do is to add those buckets in the parameter store. The parameter store is a feature in the SSM (AWS Systems Manager) that enables centralized management and security of data and secrets.

2. Add Bucket names into the parameter store.
```bash
awslocal ssm put-parameter \
    --name /localstack-thumbnail-app/buckets/images \
    --type "String" \
    --value "localstack-thumbnails-app-images"

awslocal ssm put-parameter \
    --name /localstack-thumbnail-app/buckets/resized \
    --type "String" \
    --value "localstack-thumbnails-app-resized"
```

## Create SNS DLQ Topic for failed Lambda invocations.
AWS Simple Notification Service Dead-Line Queue is a feature that allows us to handle messages that cannot be delivered to their intended subcribers. To create an SNS DLQ topic use the following.
```bash
awslocal sns create-topic --name failed-resized-topic
```

To receive immediate alerts in case of image resize failure, you have to subcribe your email address to the system. You can use the following the command:
```bash
awslocal sns subscribe \
    --topic-arn arn:aws:sns:us-east-1:000000000000:failed-resized-topic \
    --protocol email \
    --notification-endpoint your-email-address
```

## Create the Presign Lambda.
```python
(cd lambdas/presign; rm -f lambda.zip; zip lambda.zip handler.py)

awslocal lambda create-function \
    --function-name presign \
    --runtime python3.9 \
    --timeout 10 \
    --zip-file fileb://lambdas/presign/lambda.zip \
    --handler handler.handler \
    --role arn:aws:iam::000000000000:role/lambda-role \
    --environment Variables="{STAGE=local}"

awslocal lambda wait function-active-v2 --function-name presign

awslocal lambda create-function-url-config \
    --function-name presign \
    --auth-type NONE
```

## Create the image list Lambda
```python
(cd lambdas/list; rm -f lambda.zip; zip lambda.zip handler.py)

awslocal lambda create-function \
    --function-name list \
    --handler handler.handler \
    --zip-file fileb://lambdas/list/lambda.zip \
    --runtime python3.9 \
    --timeout 10 \
    --role arn:aws:iam::000000000000:role/lambda-role \
    --environment Variables="{STAGE=local}"

awslocal lambda wait function-active-v2 --function-name list

awslocal lambda create-function-url-config \
    --function-name list \
    --auth-type NONE
```

