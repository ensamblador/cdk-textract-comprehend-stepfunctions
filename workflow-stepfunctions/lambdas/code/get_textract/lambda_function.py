import logging
import json
import boto3
import os
import datetime


REGION                    = os.environ.get('REGION')
TABLE_DOCUMENTS_NAME      = os.environ.get('TABLE_DOCUMENTS_NAME')

textract                  = boto3.client('textract', region_name=REGION)
comprehend                = boto3.client('comprehend', region_name=REGION)

ddb_table                 = boto3.resource('dynamodb', region_name=REGION).Table(TABLE_DOCUMENTS_NAME)


def get_textract_corpus(blocks):
    texto = []
    for b in blocks:
        if b['BlockType'] == 'LINE':
            texto.append(b['Text'])
    corpus = ' '.join(texto)
    return corpus

def split_corpus(some_text,max_len):
    chunks = []
    current = []
    n_chars = 0
    words = some_text.split(' ')
    for word in words:
        if (n_chars + len(word) + 1)< max_len:
            n_chars += len(word) + 1
            current.append(word)
        else:
            chunks.append(' '.join(current))
            current = [word]
            n_chars = len(word) + 1
    
    chunks.append(' '.join(current))
    return chunks

def get_entities_5000(some_text):    
    lang_code='es'
    entities = comprehend.detect_entities(Text=some_text, LanguageCode=lang_code)
    return entities['Entities']

def get_key_phrases_5000(some_text):    
    lang_code='es'
    kps = comprehend.detect_key_phrases(Text=some_text, LanguageCode=lang_code)
    return kps['KeyPhrases']

def get_entities(some_text):
    entities = []
    if len(some_text)>4800:
        chunks = split_corpus(some_text, 4800)
        for chunk in chunks:
            entities += get_entities_5000(chunk)
        return entities
    else:
        return get_entities_5000(some_text)

def get_key_phrases(some_text):
    kps = []
    if len(some_text)>4800:
        chunks = split_corpus(some_text, 4800)
        for chunk in chunks:
            kps += get_key_phrases_5000(chunk)
        return kps
    else:
        return get_key_phrases_5000(some_text)

def get_nlp_features(some_text):
    entities = get_entities(some_text)
    #key_phrases = get_key_phrases(some_text)
    return {
        'Entities':[ {'Type': ent["Type"], 'Text': ent["Text"]} for ent in entities],
        #'KeyPhrases': key_phrases
    }


def update_document_text(s3_location, status,  textract_text, textract_result, nlp_entities):

    update_response = ddb_table.update_item(
        Key = {'s3_location': s3_location},
        UpdateExpression = "set textract_status = :a, textract_text = :b, textract_result = :c, nlp_entities = :d",
        ExpressionAttributeValues={
        ':a': status,
        ':b': textract_text,
        ':c': json.dumps(textract_result),
        ':d': json.dumps(nlp_entities),
        },
        ReturnValues="UPDATED_NEW"
        )
    actualizado = update_response['Attributes']['textract_status']
    print (f'datos actualizados:\n{actualizado}')
    return update_response

def get_textract_job_details(job_id):
    blocks = []
    text_detected = textract.get_document_text_detection(JobId=job_id)

    if text_detected['JobStatus'] == 'SUCCEEDED':
        res = text_detected
        blocks += res['Blocks']
        while 'NextToken' in res:
            res = textract.get_document_text_detection(JobId=job_id, NextToken = res['NextToken'])
            blocks += res['Blocks']
        print ('Blocks:', len (blocks))
    
    return {'blocks': blocks, 'JobStatus': text_detected['JobStatus'] }
    



def lambda_handler(event, context):


    print ('se recibio evento:\n',event)

    job_id = event['JobId']
    s3_location = event['s3_location']
    
    blocks    = get_textract_job_details(job_id)

    if blocks['JobStatus'] == 'IN_PROGRESS':
        return { 'corpus': '', 'JobStatus': blocks['JobStatus']}
    
    corpus    = get_textract_corpus(blocks['blocks'])

    features = get_nlp_features(corpus)

    update_document_text(s3_location,blocks['JobStatus'], corpus, blocks['blocks'], features['Entities'] )


    return {
        'corpus': f'{corpus[:100]}...',
        'JobStatus': blocks['JobStatus']
    }


