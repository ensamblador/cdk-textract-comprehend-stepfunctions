
import json
import boto3
import os
import datetime
from decimal import Decimal

REGION                   = os.environ.get('REGION')
TEXTRACT_S3_BUCKET       = os.environ.get('TEXTRACT_S3_BUCKET')
TABLE_DOCUMENTS_NAME     = os.environ.get('TABLE_DOCUMENTS_NAME')
textract                 = boto3.client('textract', region_name=REGION)
ddb_table                 = boto3.resource('dynamodb', region_name=REGION).Table(TABLE_DOCUMENTS_NAME)

def start_text_detection(bucket, object):

    document_location = {
            'S3Object': {
                'Bucket': bucket,
                'Name': object
            }
        }
    output_config = {
            'S3Bucket': TEXTRACT_S3_BUCKET,
            'S3Prefix': object
        }
    
    print ('Ducument Location:\n', document_location)
    print ('Output Config:\n', output_config)

    text_detection = textract.start_document_text_detection(
        DocumentLocation = document_location,
        #NotificationChannel={
        #    'SNSTopicArn': TRANSCRIBE_SNS_TOPIC,
        #    'RoleArn': TRANSCRIBE_SNS_ROLE
        #},
        OutputConfig=output_config
    )

    return text_detection

def update_documento(ddb_table, key, job_id):
    print (f'Actualizando Documento {key}')
    update_response = ddb_table.update_item(
        Key = key,
        UpdateExpression = "set textract_jobid = :a",
        ExpressionAttributeValues={':a': job_id},
        ReturnValues="UPDATED_NEW"
    )
    actualizado = update_response['Attributes']
    print (f'datos actualizados:\n{actualizado}')
    return update_response['Attributes']
    

def lambda_handler(event, context):

    print("Se recibió el evento", event)

    bucket      = event['bucket']
    object      = event['object']
    s3_location = event['s3_location']

    result = start_text_detection(bucket, object)
    update_documento(ddb_table, {'s3_location': s3_location}, result['JobId'])

    return result['JobId']


