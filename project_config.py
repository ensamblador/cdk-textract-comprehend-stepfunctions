
from  aws_cdk import (
    core,
    aws_lambda
)

# EDIT THIS PART

STACK_NAME = 'DEMO-TCSF'
INSIGHTS_STACK_NAME = 'DEMO-TCSF-INSIGHTS'
EMAIL = 'enrique.rodriguez.garrido@gmail.com'
OWNER_REPO = 'ensamblador/cdk-textract-comprehend-stepfunctions'
REPO_BRANCH = 'main'

# ! Crear previamente la conexión a github en codestar
# # ** https://docs.aws.amazon.com/cdk/api/latest/python/aws_cdk.pipelines/README.html#github-github-enterprise-bitbucket-using-a-connection

CONNECTION_ARN = 'arn:aws:codestar-connections:us-east-1:942104583055:connection/a1d4303b-918c-4ec9-ab6f-88d8590de494'

TAGS =  {
    "APPLICATION": "DEMO-TCSF",
    "ENVIRONMENT": "DEV",
    "GROUP": "DEMOS"
}

BASE_ENV_VARIABLES = dict(
        REGION                      = 'us-east-1',
        BASE_DOWNLOAD_PATH          = '/tmp',
        DOCUMENT_S3_PREFIX          = 'documentos',
        LOCAL_TIMEZONE              = 'America/Santiago',

)

LAMBDA_TIMEOUT= 60

BASE_LAMBDA_CONFIG = dict (
    timeout=core.Duration.seconds(LAMBDA_TIMEOUT),       
    memory_size=256,
    tracing= aws_lambda.Tracing.ACTIVE,
    description=STACK_NAME)

REMOVAL_POLICY = core.RemovalPolicy.DESTROY


# STOP EDITING!


# JK YOU CAN SET LAMBDA RUNTIME HERE ;)

PYTHON_LAMBDA_CONFIG = dict (runtime=aws_lambda.Runtime.PYTHON_3_8, **BASE_LAMBDA_CONFIG)


#Just in case of Api Gateway

BASE_INTEGRATION_CONFIG =  dict(proxy=True,
    integration_responses=[{
        'statusCode': '200',
        'responseParameters': {
            'method.response.header.Access-Control-Allow-Origin': "'*'"
        }
    }])

BASE_METHOD_RESPONSE = dict(
    method_responses=[{
        'statusCode': '200',
        'responseParameters': {
            'method.response.header.Access-Control-Allow-Origin': True,
        }
    }]
)