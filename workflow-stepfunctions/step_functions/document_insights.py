import sys
import json
sys.path.append("..")

from aws_cdk import (
    aws_s3 as s3,
    aws_iam as iam,
    aws_logs,
    aws_ssm as ssm,
    aws_stepfunctions_tasks as sf_tasks,
    aws_stepfunctions as step_fn,
    core as cdk,

)

from project_config import (
    BASE_ENV_VARIABLES,
    REMOVAL_POLICY,
    STACK_NAME
)




class InsightsStateMachine(cdk.Construct):

    def __init__(self, scope: cdk.Construct, construct_id: str,  project_lambdas, tables,**kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # ** ------------------------------------------------- **
        # ** Workflow Transcribe / Comprehend (Cada Documento) ** 
        # ** ------------------------------------------------- **


        # ** STEPS


        # ** 0) Guarda Documento en la Base de Datos
        guarda_documento_ddb = sf_tasks.DynamoPutItem(
            self, "Guarda Documento en DB", 
            item = {
                "s3_location": sf_tasks.DynamoAttributeValue.from_string(step_fn.JsonPath.string_at("$.s3_location")),
                "size": sf_tasks.DynamoAttributeValue.from_string(step_fn.JsonPath.string_at("$.size")),
            },
            table=tables.tabla_documentos,
            result_path = '$.InsertedDocument'
            )

        # ** 1) Comienza el Textract Job
        start_textract_step = sf_tasks.LambdaInvoke(self,'Start Text Detection',
            payload_response_only =True,
            lambda_function = project_lambdas.start_text_detection, 
            result_path='$.JobId')

        # ** 2) Obtiene el Textract Job Status y Corpus
        get_textract_step = sf_tasks.LambdaInvoke(self,'Get Text Detection',
            payload_response_only =True,
            lambda_function = project_lambdas.get_textract,
            result_path='$.TextractResult')

        success_state = step_fn.Succeed(self, 'OK documento')
        failed_state  = step_fn.Fail(self, 'Fallamos')
        
        wait_for_it = step_fn.Wait(self, "espera 10 segundos", time=step_fn.WaitTime.duration(cdk.Duration.seconds(10)))

        flujo_textract = guarda_documento_ddb.next(start_textract_step).next(
                wait_for_it
                ).next(get_textract_step).next(
                    step_fn.Choice(self, "Textract Succeed?")
                    .when(step_fn.Condition.string_equals("$.TextractResult.JobStatus", "IN_PROGRESS"), wait_for_it)
                    .when(step_fn.Condition.string_equals("$.TextractResult.JobStatus", "SUCCEEDED"), success_state)
                    .otherwise(failed_state).afterwards() 
                )


        definition_detalles = flujo_textract


        obtiene_insights_documentos = step_fn.StateMachine(
            self, 'ObtieneInsights', 
            logs = step_fn.LogOptions(
                destination=aws_logs.LogGroup(self, "loggroupdetails"),
                include_execution_data = True,
                level = step_fn.LogLevel.ALL
            ),
            definition=definition_detalles, 
            timeout=cdk.Duration.minutes(10),
            tracing_enabled= True
            )

        self.workflow = obtiene_insights_documentos
