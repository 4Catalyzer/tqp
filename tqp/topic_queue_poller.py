import json
import logging

import boto3

from .threading_utils import Interval

# -----------------------------------------------------------------------------


def _jsonify_dictionary(dictionary):
    return {k: json.dumps(v) for k, v in dictionary.items()}


logger = logging.getLogger(name=__name__)

# -----------------------------------------------------------------------------


def create_queue(queue_name, **kwargs):
    sqs = boto3.resource('sqs')

    def _create_queue(name, attributes):
        return sqs.create_queue(
            QueueName=name, Attributes=_jsonify_dictionary(attributes),
        )

    dead_letter_queue = _create_queue('{}-dead-letter'.format(queue_name), {
        'MessageRetentionPeriod': 1209600,  # maximum (14 days)
    })
    dead_letter_queue_arn = dead_letter_queue.attributes['QueueArn']

    redrive_policy_kwargs = kwargs.pop('RedrivePolicy', {})
    return _create_queue(queue_name, {
        'RedrivePolicy': {
            'maxReceiveCount': 5,
            **redrive_policy_kwargs,
            'deadLetterTargetArn': dead_letter_queue_arn,
        },
        **kwargs,
    })


# -----------------------------------------------------------------------------


class QueuePollerBase:
    logger = logger

    def __init__(self, queue_name, prefix=None, **kwargs):
        self.prefix = '{}--'.format(prefix) if prefix else ''
        self.queue_name = '{}{}'.format(self.prefix, queue_name)
        self.queue_attributes = kwargs

    def extend_message_visibility_timeout(self, queue, messages, timeout):
        # this is safe to run on already deleted messages, because
        # it would simply fail the operation only for the already deleted ones
        self.logger.debug("increasing message visibility")
        queue.change_message_visibility_batch(Entries=[{
            'Id': msg.message_id,
            'ReceiptHandle': msg.receipt_handle,
            'VisibilityTimeout': timeout,
        } for msg in messages])

    def ensure_queue(self):
        return create_queue(self.queue_name, **self.queue_attributes)

    def get_message_payload(msg):
        return None

    def _handle_message(self, msg):
        payload = self.get_message_payload(msg)
        try:
            self.handle_message(msg, payload)

            msg.delete()
            self.logger.debug('message successfully deleted')
        except Exception as e:
            # whatever the error is, log and move on
            self.handle_error(e, msg, payload)

    def handle_error(self, exception, msg, payload):
        self.logger.exception(
            "encountered an error when handling the following message: \n%s",
            msg.body,
        )

    def handle_message(self, msg, payload):
        raise NotImplemented()

    def start(self):
        self.logger.debug('creating queue')
        queue = self.ensure_queue()
        self.logger.info('starting to poll')

        visibility_timeout = int(queue.attributes['VisibilityTimeout'])

        while True:
            messages = queue.receive_messages(
                MessageAttributeNames=['All'],
                # maximum amount. helps for most efficient long polling
                WaitTimeSeconds=20,
                MaxNumberOfMessages=5,
            )
            self.logger.debug('received %s message(s)', len(messages))

            with Interval(
                visibility_timeout - 5, self.extend_message_visibility_timeout,
                (queue, messages, visibility_timeout),
            ):
                for msg in messages:
                    self._handle_message(msg)


# -----------------------------------------------------------------------------


class TopicQueuePoller(QueuePollerBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.handlers = {}

    def get_message_payload(self, msg):
        body = json.loads(msg.body)
        topic = body['TopicArn'].split(':')[-1]
        message = body.pop('Message')
        handler, parse_json, with_meta = self.handlers[topic]
        if parse_json:
            message = json.loads(message)

        return {
            'topic': topic,
            'handler': handler,
            'message': message,
            'meta': {
                'body': body,
                'topic': topic[len(self.prefix):],
            } if with_meta else None,
        }

    def handle_message(self, msg, payload):
        topic = payload['topic']
        handler = payload['handler']
        meta = payload['meta']
        message = payload['message']

        self.logger.info('%s: handling new message', topic)
        self.logger.debug(msg.body)

        extra_call_kwargs = {'meta': meta} if meta is not None else {}
        handler(message, **extra_call_kwargs)

    def handler(
        self,
        *topics,
        parse_json=True,
        with_meta=False,
        use_prefix=True
    ):
        def decorator(func):
            for topic in topics:
                if use_prefix:
                    topic_name = '{}{}'.format(self.prefix, topic)
                else:
                    topic_name = topic

                if topic_name in self.handlers:
                    raise ValueError(
                        'Topic {} already registered'.format(topic_name),
                    )

                self.handlers[topic_name] = func, parse_json, with_meta

            return func

        return decorator

    def ensure_queue(self):
        queue = super().ensure_queue()
        queue_arn = queue.attributes['QueueArn']

        sns = boto3.resource('sns')
        policies = []

        for topic_name in self.handlers.keys():
            topic = sns.create_topic(Name=topic_name)
            policies.append({
                'Sid': 'sns',
                'Effect': 'Allow',
                'Principal': {'AWS': '*'},
                'Action': 'SQS:SendMessage',
                'Resource': queue_arn,
                'Condition': {
                    'ArnEquals': {
                        'aws:SourceArn': topic.arn,
                    },
                },
            })

            topic.subscribe(Protocol='sqs', Endpoint=queue_arn)

        queue.set_attributes(Attributes=_jsonify_dictionary({
            'Policy': {'Version': '2012-10-17', 'Statement': policies},
        }))

        return queue
