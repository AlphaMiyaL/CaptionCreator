import csv
import boto3

# csv file is the credentials for the IAM account
# the IAM account should have FULL access to Amazon Rekognition and S3 Bucket to work properly
with open('new_user_credentials.csv', 'r') as input:
    next(input)
    reader = csv.reader(input)
    for line in reader:
        access_key_id = line[2]
        secret_access_key = line[3]

# Images should only be .jpg or .png format
# Alice.jpg is a test image
photo = 'Alice.png'

client = boto3.client('rekognition',
                      region_name='us-west-2',
                      aws_access_key_id=access_key_id,
                      aws_secret_access_key=secret_access_key)
with open(photo, 'rb') as source_image:
    source_bytes = source_image.read()  # Convert image to bytes

response = client.detect_labels(Image={'Bytes': source_bytes},  # if taking img from project src, use this line
                                # Image={'S3Object': {  # if taking img from S3 Bucket, use these lines
                                #     'Bucket': '',  # name of the S3 bucket
                                #     'Name': '',  # name of the img file in the bucket
                                #     'Version': ''  # only needed of bucket has versioning enabled
                                # }},
                                MaxLabels=10,  # limits the labels returned
                                MinConfidence=95)  # returns only labels that have confidence level > amount specified
print(response)
