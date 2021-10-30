import json
from aws_cdk import (
    aws_s3 as s3,
    aws_iam as iam,
    aws_logs,
    aws_ssm as ssm,
    aws_stepfunctions_tasks as sf_tasks,
    aws_stepfunctions as step_fn,
    aws_s3_notifications as s3n,
    core as cdk,

)
# For consistency with other languages, `cdk` is the preferred import name for
# the CDK's core module.  The following line also imports it as `core` for use
# with examples from the CDK Developer's Guide, which are in the process of
# being updated to use `cdk`.  You may delete this import if you don't need it.
from aws_cdk import core

from project_config import (
    BASE_ENV_VARIABLES,
    REMOVAL_POLICY,
    STACK_NAME
)

from lambdas.project_lambdas import Lambdas
from databases.databases import DDBTables
from buckets.buckets import Buckets
from sqs.sqs import SQSQueue
from step_functions.document_insights import InsightsStateMachine


class WorkflowStepfunctionsStack(cdk.Stack):

    def __init__(self, scope: cdk.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)



        project_tables = DDBTables(self, 'Tables')
        project_buckets = Buckets(self, "Buckets")
        sqs_queue = SQSQueue(self, 'procesar', 60)



        LOCAL_ENV_VARIABLES = json.loads(json.dumps(dict(
            TEXTRACT_S3_BUCKET = project_buckets.textract_bucket.bucket_name,
            QUEUE_URL = sqs_queue.queue.queue_url,
            DOCUMENT_S3_BUCKET = project_buckets.documents_bucket.bucket_name,
            TABLE_DOCUMENTS_NAME = project_tables.tabla_documentos.table_name,
            **BASE_ENV_VARIABLES )))


        project_lambdas = Lambdas(self, 'insights_lambdas', LOCAL_ENV_VARIABLES)

        project_tables.tabla_documentos.grant_read_write_data(project_lambdas.start_text_detection)
        project_tables.tabla_documentos.grant_read_write_data(project_lambdas.get_textract)


        # ** Permisos para los buckets de origen y resultados

        project_lambdas.start_text_detection.add_to_role_policy(
            iam.PolicyStatement(actions=["s3:*"],resources=[
                    project_buckets.documents_bucket.bucket_arn+'/*', 
                    project_buckets.textract_bucket.bucket_arn+'/*']))

        project_lambdas.start_text_detection.add_to_role_policy(
            iam.PolicyStatement(actions=["Textract:*"], resources=['*']))

        project_lambdas.get_textract.add_to_role_policy(
            iam.PolicyStatement(actions=["Textract:*"], resources=['*']))

        project_lambdas.get_textract.add_to_role_policy(
            iam.PolicyStatement(actions=["s3:*"],
            resources=[project_buckets.documents_bucket.bucket_arn+'/*', 
            project_buckets.textract_bucket.bucket_arn+'/*']))

        project_lambdas.get_textract.add_to_role_policy(
            iam.PolicyStatement(actions=["Comprehend:*"], resources=['*']))



        # ** Cada vez que se crea un objeto, se envia un mensaje a la cola.
    
        project_buckets.documents_bucket.add_event_notification(
            s3.EventType.OBJECT_CREATED, s3n.SqsDestination(sqs_queue.queue))

        # ** Y la cola gatilla esta lambda que comieza el proceso...

        sqs_queue.trigger(project_lambdas.get_message_for_details)

        # ** La step function...

        step_function = InsightsStateMachine(self, "insights_workflow", project_lambdas, project_tables)

        # ** La lambda que comienza el procesamiento...

        project_lambdas.get_message_for_details.add_environment(
            key='STATE_MACHINE_ARN', value=step_function.workflow.state_machine_arn)

        step_function.workflow.grant_start_execution(
            project_lambdas.get_message_for_details
        )


