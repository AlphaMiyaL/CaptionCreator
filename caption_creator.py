import csv
import boto3
from rekognition import Rekognition

rk_client = Rekognition('new_user_credentials.csv')
rk_client.replace_photo('faces.jpg')
rk_client.detect_labels(10, 95)
rk_client.print_labels()
rk_client.detect_moderation_labels(0)
rk_client.print_labels()
rk_client.detect_faces('ALL')
rk_client.print_labels()
