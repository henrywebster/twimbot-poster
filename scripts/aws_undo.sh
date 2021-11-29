#!/usr/bin/env bash

# Reset the entry as unposted in DynamoDB
# Usage: ./aws_undo.sh <file name (DB key)>

# TODO: also delete from Twitter using cURL

# A .env file is expected in the parent directory defining $DYNAMODB_TABLE
source ../.env

KEY=$1
TIME=$(date +%s)

aws dynamodb update-item \
    --table-name $DYNAMODB_TABLE \
    --key "{\"id\": {\"S\": \"$KEY\"}}" \
    --update-expression "ADD process_time :t" \
    --expression-attribute-values "{\":t\": {\"N\": \"$TIME\"}}" \