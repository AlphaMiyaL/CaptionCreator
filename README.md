# CaptionCreator
Generates captions for images, using Amazon Rekognition to identify the objects and actions depicted in the image

## Imports
boto3 <br /> 
python 3.10.8

## AWS requirements
Needs a IAM account with Full Access to S3 Bucket and Amazon Rekognition <br />
Needs the .csv file for the IAM account in the project source folder

## Instructions
Images should be put in the S3 bucket, or in the source folder <br />
Create an instance of the Rekognition class, and pass in the .csv file <br />
Pass in name of photo using replace_photo <br />
Use set_s3 to set use_s3 to true if using images from S3 bucket

