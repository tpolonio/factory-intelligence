#!/bin/bash
echo "=========== [FACTORY INTELLIGENCE] CREATING LOCAL AWS RESOURCES ==========="

# Cria o bucket S3 exato da configuração da API
awslocal s3 mb s3://factory-intelligence-reports

# Cria a fila SQS exata da configuração da API
awslocal sqs create-queue --queue-name factory-intelligence-reports-queue

echo "=========== [FACTORY INTELLIGENCE] AWS RESOURCES READY ==========="