#!/usr/bin/env python3
import os

from aws_cdk import core as cdk

# For consistency with TypeScript code, `cdk` is the preferred import name for
# the CDK's core module.  The following line also imports it as `core` for use
# with examples from the CDK Developer's Guide, which are in the process of
# being updated to use `cdk`.  You may delete this import if you don't need it.
from aws_cdk import core


from cdk_pipeline.cdk_pipeline_stack import CdkPipelineStack
from workflow_stepfunctions.workflow_stepfunctions_stack import WorkflowStepfunctionsStack
from project_config import TAGS, STACK_NAME



# **  Si quiere agregar o modificar el ci/cd pipeline para el manejo de esta aplicación
# **  Primero lea completamente https://docs.aws.amazon.com/cdk/api/latest/python/aws_cdk.pipelines/README.html
# **  comente `WorkflowStepfunctionsStack(app, f'{STACK_NAME.upper()}',` y 
# **  descomente `CdkPipelineStack(app, f'{STACK_NAME.upper()}-PIPELINE',` para desplegar el pipeline de CI/CD


app = core.App()
cdk_pipeline_stack = CdkPipelineStack(app, f'{STACK_NAME.upper()}-PIPELINE',
#workflow_stack = WorkflowStepfunctionsStack(app, f'{STACK_NAME.upper()}',
    # If you don't specify 'env', this stack will be environment-agnostic.
    # Account/Region-dependent features and context lookups will not work,
    # but a single synthesized template can be deployed anywhere.

    # Uncomment the next line to specialize this stack for the AWS Account
    # and Region that are implied by the current CLI configuration.

    #env=core.Environment(account=os.getenv('CDK_DEFAULT_ACCOUNT'), region=os.getenv('CDK_DEFAULT_REGION')),

    # Uncomment the next line if you know exactly what Account and Region you
    # want to deploy the stack to. */

    #env=core.Environment(account='123456789012', region='us-east-1'),

    # For more information, see https://docs.aws.amazon.com/cdk/latest/guide/environments.html
    )


if TAGS.keys():
    for k in TAGS.keys():
        core.Tag.add(app,k,TAGS[k])

app.synth()
