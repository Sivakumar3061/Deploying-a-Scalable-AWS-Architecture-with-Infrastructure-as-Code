import boto3

bucket_name = "awsproject-aishwariya-bucket-12022025"   # or any unique name you like

# Client in us-east-1
s3 = boto3.client("s3", region_name="us-east-1")

def create_bucket():
    response = s3.create_bucket(
        Bucket=bucket_name   # NO CreateBucketConfiguration here
    )
    print("Bucket created:", response)

if __name__ == "__main__":
    create_bucket()
