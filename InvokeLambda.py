import boto3
import json

client = boto3.client("lambda", region_name="us-east-1")

resp = client.invoke(
    FunctionName="project-s3-upload-logger",
    Payload=json.dumps({"test": "boto3 invoke"})
)

print(resp["StatusCode"])
print(resp["Payload"].read().decode())
