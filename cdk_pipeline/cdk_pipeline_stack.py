from aws_cdk import (
    aws_sns as sns,
    aws_sns_subscriptions as subs,
    pipelines as pipe, 
    aws_codepipeline_actions as codepipeline_actions,
    core as cdk)

from workflow_stepfunctions.workflow_stepfunctions_stack import WorkflowStepfunctionsStack


from project_config import TAGS, STACK_NAME, EMAIL, OWNER_REPO, REPO_BRANCH, CONNECTION_ARN


class CdkPipelineStack(cdk.Stack):

    def __init__(self, scope: cdk.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)


        topic = sns.Topic(self, "SecurityChangesTopic")
        topic.add_subscription(subs.EmailSubscription(EMAIL))


        source  = pipe. CodePipelineSource.connection(OWNER_REPO, REPO_BRANCH,
        
        connection_arn= CONNECTION_ARN
        )

        pipeline =  pipe.CodePipeline(self, "Pipeline", 
                        pipeline_name="textrac-workflow-cicd",
                        synth=pipe.ShellStep("Synth", 
                            input=source,
                            #descomenta si es un subdirectorio por ejemplo workflow-stepfunctions
                            #primary_output_directory= 'workflow-stepfunctions/cdk.out',
                            commands=["npm install -g aws-cdk", 
                            #descomenta si es un subdirectorio por ejemplo workflow-stepfunctions
                            #    "cd workflow-stepfunctions",
                                "python -m pip install -r requirements.txt", 
                                f"cdk synth {STACK_NAME.upper()}"]
                        )
                    )
        pipeline.add_stage(CodeApplication(self, ))


class CodeApplication(cdk.Stage):
    def __init__(self, scope, id, *, env=None, outdir=None):
        super().__init__(scope, id, env=env, outdir=outdir)

        WorkflowStepfunctionsStack(self, f'{STACK_NAME.upper()}-TEST')