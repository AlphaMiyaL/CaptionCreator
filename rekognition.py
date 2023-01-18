import csv
import boto3


class Rekognition:
    def __init__(self, csv_file):
        # csv file is the credentials for the IAM account
        # the IAM account should have FULL access to Amazon Rekognition and S3 Bucket to work properly
        with open(csv_file, 'r') as input:
            next(input)
            reader = csv.reader(input)
            for line in reader:
                access_key_id = line[2]
                secret_access_key = line[3]
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
    def replace_photo(self, photo):
        self.photo = photo
        with open(photo, 'rb') as source_image:
            self.source_bytes = source_image.read()  # Convert image to bytes

    def replace_photo2(self, bytes):
        self.source_bytes = bytes

    # replaces photo used to compare in compare_faces
    def replace_comparing_photo(self, photo):
        self.photo2 = photo
        with open(photo, 'rb') as source_image:
            self.source_bytes2 = source_image.read()  # Convert image to bytes

    def set_s3(self, val):
        self.use_s3 = val

    def detect_labels(self, max_labels, min_confidence):
        if self.use_s3:
            self.response = self.client.detect_labels(
                Image={'S3Object': {  # if img from S3 Bucket, use these lines
                    'Bucket': '',  # name of the S3 bucket
                    'Name': self.photo,  # name of the img file in the bucket
                    # 'Version': ''  # only needed of bucket has versioning enabled
                }},
                MaxLabels=max_labels,  # limits the labels returned
                MinConfidence=min_confidence)  # returns only labels with confidence >
        else:
            self.response = self.client.detect_labels(
                Image={'Bytes': self.source_bytes},  # if img from proj src, use this line
                MaxLabels=max_labels,  # limits the labels returned
                MinConfidence=min_confidence)  # returns only labels with confidence >

    # use detect_moderation_labels if wanting to moderate photos of explicit content
    # moderation labels return labels that are classified as suggestive or explicit, moderator can decide what to do
    # contains minConfidence as a parameter to return
    def detect_moderation_labels(self, min_confidence):
        if self.use_s3:
            self.response = self.client.detect_moderation_labels(
                Image={'S3Object': {  # if img from S3 Bucket, use these lines
                    'Bucket': '',  # name of the S3 bucket
                    'Name': self.photo,  # name of the img file in the bucket
                    # 'Version': ''  # only needed of bucket has versioning enabled
                }},
                MinConfidence=min_confidence)  # returns only labels with confidence >
        else:
            self.response = self.client.detect_moderation_labels(
                Image={'Bytes': self.source_bytes},  # if img from proj src, use this line
                MinConfidence=min_confidence)  # returns only labels with confidence >

    # Detects faces in image and the attributes of the face
    # Attributes parameter exists to specify which attributes wanted for return
    # If nothing passed in, will use DEFAULT as attribute
    def detect_faces(self, att):
        if self.use_s3:
            self.response = self.client.detect_faces(
                Image={'S3Object': {  # if img from S3 Bucket, use these lines
                    'Bucket': '',  # name of the S3 bucket
                    'Name': self.photo,  # name of the img file in the bucket
                    # 'Version': ''  # only needed of bucket has versioning enabled
                }},
                Attributes=[att])  # Array of facial attributes wanted to be returned; ALL -> all facial attributes
        else:
            self.response = self.client.detect_faces(
                Image={'Bytes': self.source_bytes},  # if img from proj src, use this line
                Attributes=[att])  # Array of facial attributes wanted to be returned; ALL -> all facial attributes

    # recognizes celebrities and returns their URls to who they are
    # sometimes inaccurate
    def recognize_celebrities(self):
        if self.use_s3:
            self.response = self.client.recognize_celebrities(
                Image={'S3Object': {  # if img from S3 Bucket, use these lines
                    'Bucket': '',  # name of the S3 bucket
                    'Name': self.photo,  # name of the img file in the bucket
                    # 'Version': ''  # only needed of bucket has versioning enabled
                }}, )
        else:
            self.response = self.client.recognize_celebrities(
                Image={'Bytes': self.source_bytes})  # if img from proj src, use this line

    # compares faces in source and target images and returns whether faces match or not with confidence value
    def compare_faces(self):
        if self.use_s3:
            self.response = self.client.compare_faces(
                SourceImage={
                    'S3Object': {  # if img from S3 Bucket, use these lines
                        'Bucket': '',  # name of the S3 bucket
                        'Name': self.photo,  # name of the img file in the bucket
                        # 'Version': ''  # only needed of bucket has versioning enabled
                    }},
                TargetImage={
                    'S3Object': {  # if img from S3 Bucket, use these lines
                        'Bucket': '',  # name of the S3 bucket
                        'Name': self.photo2,  # name of the img file in the bucket
                        # 'Version': ''  # only needed of bucket has versioning enabled
                    }},
            )
        else:
            self.response = self.client.compare_faces(
                SourceImage={'Bytes': self.source_bytes},  # if img from proj src, use this line
                TargetImage={'Bytes': self.source_bytes2}
            )

    # detects text in images and returns said text
    def detect_text(self):
        if self.use_s3:
            self.response = self.client.detect_text(
                Image={'S3Object': {  # if img from S3 Bucket, use these lines
                    'Bucket': '',  # name of the S3 bucket
                    'Name': self.photo,  # name of the img file in the bucket
                    # 'Version': ''  # only needed of bucket has versioning enabled
                }}, )
        else:
            self.response = self.client.detect_text(
                Image={'Bytes': self.source_bytes})  # if img from proj src, use this line

    def print_labels(self):
        use_default = None
        for key, value in self.response.items():
            if key == 'FaceDetails':
                for people_att in value:
                    print(people_att)
                    print("======")
            elif key == 'CelebrityFaces':
                for people in value:
                    print(people)
            elif key in ('FaceMatches', 'UnmatchedFaces'):
                print(key)
                for att in value:
                    print(att)
            else:
                use_default = True
                break
        if use_default:
            print(self.response)
