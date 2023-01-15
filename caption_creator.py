import csv
import boto3
from rekognition import Rekognition

# Must pass in csv file for IAM account containing Full Access of AWS Rekognition and S3 Bucket
rk_client = Rekognition('new_user_credentials.csv')
rk_client.replace_photo('images/rock_and_hart.jpg')
# rk_client.detect_labels(10, 95)
# rk_client.print_labels()
# rk_client.detect_moderation_labels(0)
# rk_client.print_labels()
# rk_client.detect_faces('ALL')
# rk_client.print_labels()
rk_client.recognize_celebrities()
rk_client.print_labels()
