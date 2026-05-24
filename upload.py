import boto3

s3 = boto3.client("s3")
bucket_name = "awsproject-aishwariya-bucket-12022025"

def upload_file():
    s3.upload_file("test_upload.txt", bucket_name, "test_upload.txt")
    print("Upload complete.")

upload_file()
