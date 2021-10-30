
import json
import boto3
import os

REGION                   = os.environ.get('REGION')
STATE_MACHINE_ARN        = os.environ.get('STATE_MACHINE_ARN')

sf                       = boto3.client('stepfunctions', region_name=REGION)

def process_document(doc, rh):
    
    event_time = doc['eventTime']
    bucket  = doc['s3']['bucket']['name']
    object  = doc['s3']['object']['key']
    size  = doc['s3']['object']['size']

    state_machine_input = {
        "created_at": event_time,
        "bucket": bucket,
        "s3_location": f's3://{bucket}/{object}',
        "object": object,
        "size": str(size),
        "ReceiptHandle" :rh,
    }


    response = sf.start_execution(
        stateMachineArn=STATE_MACHINE_ARN,
        input=json.dumps(state_machine_input)
    )

    print (f"StateMachineExec {response}")

def process_record(record):
    receipt_handle = record['receiptHandle']
    
    body = record['body']
    parsed_body = json.loads(body)

    if not 'Records' in parsed_body:
        print ('no hay archivos')
        return


    for documento in parsed_body['Records']:
        process_document(documento, receipt_handle)





def lambda_handler(event, context):

    print("Se recibió el evento", event)

    if not 'Records' in event:
        print ('no records...')
        return { 'statusCode': 200, 'body': event }
    
    for rec in event['Records']:
        process_record(rec)



    return { 'statusCode': 200, 'body': 'OK' }
    
  







