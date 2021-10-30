import json
import sys 

from aws_cdk import (
    aws_lambda,
    aws_ec2 as ec2,
    core as cdk,

)

sys.path.append("..")

from project_config import (
    PYTHON_LAMBDA_CONFIG,

)


class Lambdas(cdk.Construct):

    def __init__(self, scope: cdk.Construct, construct_id: str, env_vars, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        COMMON_LAMBDA_CONF = dict(
            code=aws_lambda.Code.asset("./lambdas/code"),**PYTHON_LAMBDA_CONFIG, environment= env_vars)

        self.get_message_for_details = aws_lambda.Function(
            self, "get_message_for_details", handler="get_message_for_details/lambda_function.lambda_handler",**COMMON_LAMBDA_CONF)

        self.start_text_detection = aws_lambda.Function(
            self, "start_text_detection", handler="start_textract/lambda_function.lambda_handler",**COMMON_LAMBDA_CONF)

        self.get_textract = aws_lambda.Function(
            self, "get_textract", handler="get_textract/lambda_function.lambda_handler",**COMMON_LAMBDA_CONF)
