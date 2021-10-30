
from aws_cdk import (
    aws_dynamodb as ddb,
    core as cdk,

)

from project_config import (

    REMOVAL_POLICY,

)


class DDBTables(cdk.Construct):

    def __init__(self, scope: cdk.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)


        # The code that defines your stack goes here
        tabla_documentos = ddb.Table(
            self, "documentos", partition_key=ddb.Attribute(name="s3_location", type=ddb.AttributeType.STRING),
            removal_policy=REMOVAL_POLICY)



        self.tabla_documentos = tabla_documentos

