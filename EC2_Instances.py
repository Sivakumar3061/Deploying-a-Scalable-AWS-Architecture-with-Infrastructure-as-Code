import boto3

ec2 = boto3.client("ec2", region_name="us-east-1")

def list_instances():
    resp = ec2.describe_instances()
    for r in resp["Reservations"]:
        for inst in r["Instances"]:
            print(inst["InstanceId"], inst["State"]["Name"])

list_instances()
