import boto3

# Your EC2 instance details
region = "us-east-2"  
instance_id = "i-0666d75cbe30ef779"

ec2 = boto3.client("ec2", region_name=region)

def get_instance_metadata():
    # Describe the EC2 instance
    response = ec2.describe_instances(InstanceIds=[instance_id])
    instance = response["Reservations"][0]["Instances"][0]

    print("---- EC2 INSTANCE METADATA ----")
    print("Instance ID:       ", instance["InstanceId"])
    print("Instance Type:     ", instance["InstanceType"])
    print("State:             ", instance["State"]["Name"])
    print("AMI ID:            ", instance["ImageId"])
    print("Availability Zone: ", instance["Placement"]["AvailabilityZone"])
    print("Private IP:        ", instance.get("PrivateIpAddress"))
    print("Public IP:         ", instance.get("PublicIpAddress"))
    print("VPC ID:            ", instance.get("VpcId"))
    print("Subnet ID:         ", instance.get("SubnetId"))

if __name__ == "__main__":
    get_instance_metadata()
