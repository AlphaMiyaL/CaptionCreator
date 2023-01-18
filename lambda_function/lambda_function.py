import os
from base64 import b64decode

import boto3
import openai

print('initializing function')

MAX_FILESIZE = 5 * 1024 * 1024
# DIMENSION_MIN = 80
# DIMENSION_MAX = 10000

format_output = lambda output: {
    'statusCode': output.status,
    'headers': {
        'Content-Type': 'text/plain',
    },
    'body': output.body
}


def filesize_error(output):
    output.status = 403
    output.body = 'File provided exceeded 5MB.'


def invalid_upload_error(output):
    output.status = 403
    output.body = 'Invalid file was uploaded.'


def service_unavailable_error(output):
    output.status = 503
    output.body = 'Service unavailable.'


def calculate_filesize(output):
    """
    calculates the raw filesize from base64 string
    """
    length = len(output.body)
    size = length * 4 / 3

    # add padding bytes
    remainder = length % 3
    if remainder > 0:
        size += 3 - remainder

    return size


# cache base64 string prefixes for valid filetypes
def base64_prefixes():
    accepted_filetypes = ['image/png', 'image/jpeg']

    prefixes = [None] * len(accepted_filetypes)
    for i, value in enumerate(accepted_filetypes):
        value = f'data:{value};base64,'
        prefixes[i] = (value, len(value))

    return prefixes


base64_prefixes = base64_prefixes()


def prep_base64_image(output):
    """
    validates and removes the prefix of the base64 string
    """

    for prefix, length in base64_prefixes:
        if output.body.startswith(prefix):
            output.body = output.body[length:]
            return

    invalid_upload_error(output)


def decode_base64_image(output):
    """
    decode base64 string to bytes
    """
    try:
        output.body = b64decode(output.body)
    except:
        invalid_upload_error(output)


def process_base64_image(output):
    """
    convert base64 string to bytes
    """
    prep_base64_image(output)
    if output.status != 200:
        return

    decode_base64_image(output)
    if output.status != 200:
        return

    # check filesize
    filesize = calculate_filesize(output)
    if filesize > MAX_FILESIZE:
        filesize_error(output)


def generate_labels(output, max_labels, min_confidence):
    client = None
    try:
        client = Rekognition(os.environ['AWS_ACCESS_KEY_ID'], os.environ['AWS_SECRET_ACCESS_KEY'])
    except:
        service_unavailable_error(output)
        return

    # get best matching label names
    labels = None
    try:
        client.replace_photo(output.body)
        client.detect_labels(max_labels, min_confidence)
    except:
        service_unavailable_error(output)
        return

    output.body = ', '.join(label['name'] for label in labels['Labels'])


def generate_caption(output):
    try:
        openai.api_key = os.environ['OPENAI_API_KEY']

        # build GPT-3 prompt
        prompt = f"Caption for an image with labels: {output.body}"

        # generate caption
        response = openai.Completion.create(engine="text-davinci-002", prompt=prompt)
        output.body = response["choices"][0]["text"]
    except:
        service_unavailable_error(output)


def main(output):
    process_base64_image(output)
    if output.status != 200:
        return

    generate_labels(output, 10, 95)
    if output.status != 200:
        return

    generate_caption(output)


class Output:
    __slots__ = ('status', 'body')

    def __init__(self):
        self.status = 200
        self.body = ''


def lambda_handler(event, context):
    output = Output()

    if 'body' in event:
        output.body = event['body']
        main(output)
    else:
        invalid_upload_error(output)

    return format_output(output)


print('initialized')


class Rekognition:
    def __init__(self, access_key_id, secret_access_key):
        # csv file is the credentials for the IAM account
        # the IAM account should have FULL access to Amazon Rekognition and S3 Bucket to work properly
        self.client = boto3.client('rekognition',
                                   region_name='us-west-2',
                                   aws_access_key_id=access_key_id,
                                   aws_secret_access_key=secret_access_key)
        self.use_s3 = False
        self.photo = None
        self.source_bytes = None
        self.photo2 = None
        self.source_bytes2 = None
        self.response = None

    # Images should only be .jpg or .png format
    def replace_photo(self, photo_bytes):
        self.source_bytes = photo_bytes

    def detect_labels(self, max_labels, min_confidence):
        self.response = self.client.detect_labels(
            Image={'Bytes': self.source_bytes},  # if img from proj src, use this line
            MaxLabels=max_labels,  # limits the labels returned
            MinConfidence=min_confidence)  # returns only labels with confidence >
