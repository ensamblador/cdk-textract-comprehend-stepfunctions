from aws_cdk import (
    core,
    aws_sqs as sqs,
    aws_lambda_event_sources
)

class SQSQueue(core.Construct):
    def __init__(self, scope: core.Construct, id: str, visibility_timeout=30, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        queue_fail = sqs.Queue(
            self, 'fail',
             visibility_timeout=core.Duration.seconds(visibility_timeout))

        dlq = sqs.DeadLetterQueue(max_receive_count=15, queue=queue_fail)

        queue = sqs.Queue(self, 'queue',  visibility_timeout=core.Duration.seconds(
            visibility_timeout), dead_letter_queue=dlq)

        self.queue = queue
        self.queue_fail = queue_fail
    
    def trigger (self, lambda_function):
        self.queue.grant_consume_messages(lambda_function)
        event_source = aws_lambda_event_sources.SqsEventSource(self.queue, batch_size=1)
        lambda_function.add_event_source(event_source)

    


