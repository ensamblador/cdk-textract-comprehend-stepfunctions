
from aws_cdk import (
    aws_s3 as s3,
    core as cdk,

)

from project_config import (

    REMOVAL_POLICY,

)


class Buckets(cdk.Construct):

    def __init__(self, scope: cdk.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)


        # The code that defines your stack goes here
        self.textract_bucket = s3.Bucket(self, 'textract', versioned=False, removal_policy=REMOVAL_POLICY)
        self.documents_bucket = s3.Bucket(self, 'documents', versioned=False, removal_policy=REMOVAL_POLICY)

