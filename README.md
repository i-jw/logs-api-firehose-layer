# Logs API Firehose Lambda Extension Demo

This is a demo of the logging functionality available with [AWS Lambda](https://aws.amazon.com/lambda/) Extensions to send logs directly from Lambda to [Amazon Kinesis Data Firehose(Firehose delivery stream)](https://aws.amazon.com/kinesis/data-firehose).

For more information on the extensions logs functionality, see the blog post [Using AWS Lambda extensions to send logs to custom destinations](https://aws.amazon.com/blogs/compute/using-aws-lambda-extensions-to-send-logs-to-custom-destinations/)

> This is a simple example extension to help you start investigating the Lambda Runtime Logs API. This code is not production ready, and it has never intended to be. Use it with your own discretion after testing thoroughly.  

The extension uses the Extensions API to register for INVOKE and SHUTDOWN events. The extension, using the Logs API, then subscribes to receive platform and function logs, but not extension logs. The extension runs a local HTTP endpoint listening for HTTP POST events. Lambda delivers log batches to this endpoint. The code can be amended (see the comments) to handle each log record in the batch. This can be used to process, filter, and route individual log records to any preferred destination

The example creates a lambda layer put logs to firehose delivery streams . A Lambda function is configured with an environment variable ( FIREHOSE_DELIVERY_STREAM )to specify the delivery stream name. Lambda streams the logs to the extension. The extension copies the logs to the delivery stream.

The extension uses the Python runtime from the execution environment to show the functionality. The recommended best practice is to compile your extension into an executable binary and not rely on the runtime.

The demo deploys all components together using the [AWS Serverless Application Model (AWS SAM)](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html)

## Requirements

* [AWS SAM CLI ](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html) - **minimum version 0.48**.

## Installation instructions

1. [Create an AWS account](https://portal.aws.amazon.com/gp/aws/developer/registration/index.html) if you do not already have one and login.

2. [Creating an Amazon Kinesis Data Firehose Delivery Stream](https://docs.aws.amazon.com/firehose/latest/dev/basic-create.html) make notes of STREAM_NAME

3.	create a lambda function Environment variable FIREHOSE_DELIVERY_STREAM as key, step 2 STREAM_NAME as value

4. update function execute iam role policy add follow add  "firehose:PutRecord","firehose:PutRecordBatch" in policy action

4. Clone the repo onto your local development machine:

```bash
git clone https://github.com/jw1i/logs-api-firehose-layer.git
cd logs-api-firehose-layer 
```

1. Run the following command for AWS SAM to deploy the components as specified in the `template.yml` file:
```bash
sam build
# If you don't have 'Python' or 'make' installed, you can use the option to build using a container which uses a python3.8 Docker container image
# sam build --use-container
sam deploy --stack-name firehose-logs-extension --guided
```

During the prompts:

* Accept the default Stack Name `firehose-logs-extension`.
* Enter your preferred Region
* Accept the defaults for the remaining questions.

AWS SAM deploys the application stack which includes the Lambda function and an IAM Role. AWS SAM creates a layer for the runtime, a layer for the extension, and adds them to the function.

Note the outputted ExtensionsLayer Value .

## Add the newly created layer version to a Python 3.8 runtime Lambda function.

## Invoke the Lambda function
You can now invoke the Lambda function. Amend the Region and use the following command:
```bash
aws lambda update-function-configuration --region <use your region> --function-name <your function name> --layers <LayerVersionArn from previous step>
```
The logging extension also receives the log stream directly from Lambda, and put records to kinesis firehose stream.

Browse to the [Amazon Kinesis Data Firehose](https://console.aws.amazon.com/firehose). Navigate to the Amazon Kinesis Data Firehose Delivery Stream Console Monitor the stream data collect. 

Downloading the file object containing the copied log stream. The log contains the same platform and function logs, but not the extension logs, as specified during the subscription.
