#!/bin/bash
echo "=========== [FACTORY INTELLIGENCE] CREATING LOCAL AWS RESOURCES ==========="

# Create S3 bucket for the reports
awslocal s3 mb s3://factory-intelligence-reports

# Create SQS queue for the reports
awslocal sqs create-queue --queue-name factory-intelligence-reports-queue

echo "=========== [FACTORY INTELLIGENCE] AWS RESOURCES READY ==========="