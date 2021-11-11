import json
import boto3
from urllib.parse import unquote_plus

def lambda_handler(event, context):

    # Loop through objects for this event
    for record in event['Records']:

        # Get bucket and photo (key) from S3 event object
        bucket = record['s3']['bucket']['name']
        photo = unquote_plus(record['s3']['object']['key'])
        #print('bucket:' + bucket + ', photo:' + photo)
    
        # Instantiate Rekognition client via AWS Python SDK (boto3)
        client = boto3.client('rekognition')
    
        # Call client passing S3 parameters, capturing response
        response = client.detect_labels(Image={'S3Object': {'Bucket': bucket, 'Name': photo}}, MaxLabels=10)    
    
        # Print the detected labels from Rekognition
        print('Detected labels for ' + photo + ':') 
        for label in response['Labels']:
            print ("Label: " + label['Name'] + ", Confidence: " + str(label['Confidence']))

