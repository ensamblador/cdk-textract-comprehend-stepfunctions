from aws_cdk import (
    aws_codepipeline_actions as codepipeline_actions,
    core as cdk)
from aws_cdk.pipelines import CodePipeline, CodePipelineSource, ShellStep

from workflow_stepfunctions.workflow_stepfunctions_stack import WorkflowStepfunctionsStack




class CdkPipelineStack(cdk.Stack):

    def __init__(self, scope: cdk.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        source   = CodePipelineSource.git_hub(
            "ensamblador/cdk-textract-comprehend-stepfunctions", "main",
             authentication=None)
        source  = CodePipelineSource.connection("ensamblador/cdk-textract-comprehend-stepfunctions", "main",
        connection_arn="arn:aws:codestar-connections:us-east-1:942104583055:connection/a1d4303b-918c-4ec9-ab6f-88d8590de494"
        )

        pipeline =  CodePipeline(self, "Pipeline", 
                        pipeline_name="textrac-workflow-cicd",
                        synth=ShellStep("Synth", 
                            input=source,
                            primary_output_directory= 'workflow-stepfunctions/cdk.out',
                            commands=["npm install -g aws-cdk", 
                                "cd workflow-stepfunctions",
                                "python -m pip install -r requirements.txt", 
                                "cdk synth"]
                        )
                    )
        pipeline.add_stage(CodeApplication(self, "Test"))


class CodeApplication(cdk.Stage):
    def __init__(self, scope, id, *, env=None, outdir=None):
        super().__init__(scope, id, env=env, outdir=outdir)

        WorkflowStepfunctionsStack(self, "Test")