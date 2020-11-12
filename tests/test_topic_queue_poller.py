import json
import time
from threading import Thread
from unittest.mock import Mock

import boto3
from moto import mock_s3, mock_sns, mock_sqs
from moto.server import backends

from tqp.topic_queue_poller import TopicQueuePoller, create_queue

# -----------------------------------------------------------------------------

sqs_backends = backends.get_backend("sqs")


@mock_sqs
def test_create_queue():
    create_queue("foo", tags={"my": "tag"})

    queue = sqs_backends["us-east-1"].queues["foo"]
    dlq = sqs_backends["us-east-1"].queues["foo-dead-letter"]

    assert queue.tags == {"tqp": "true", "dlq": "false", "my": "tag"}
    assert dlq.tags == {"tqp": "true", "dlq": "true", "my": "tag"}
    assert queue.redrive_policy == {
        "maxReceiveCount": 5,
        "deadLetterTargetArn": "arn:aws:sqs:us-east-1:123456789012:foo-dead-letter",
    }


@mock_sqs
@mock_sns
def test_tqp():
    poller = TopicQueuePoller("foo", prefix="test")

    handled_item = None

    @poller.handler("my_event")
    def handle_my_event(item):
        nonlocal handled_item
        handled_item = item

    t = Thread(target=poller.start, daemon=True)
    t.start()

    # making sure poller is polling
    time.sleep(0.1)

    boto3.client("sns").publish(
        TopicArn="arn:aws:sns:us-east-1:123456789012:test--my_event",
        Message='{"bar": "baz"}',
    )

    # making sure message is processed
    time.sleep(0.05)

    assert handled_item == {"bar": "baz"}


@mock_sqs
@mock_s3
def test_s3():
    s3 = boto3.client("s3")
    s3.create_bucket(Bucket="bucket_foo")

    poller = TopicQueuePoller("foo", prefix="test")

    handled_item = None

    @poller.s3_handler("bucket_foo")
    def handle_my_event(item):
        nonlocal handled_item
        handled_item = item

    t = Thread(target=poller.start, daemon=True)
    t.start()

    # making sure poller is polling
    time.sleep(0.5)

    poller._handle_message(
        Mock(
            body=json.dumps(
                {
                    "Records": [
                        {
                            "eventSource": "aws:s3",
                            "eventName": "ObjectCreated:Put",
                            "s3": {
                                "bucket": {"name": "bucket_foo"},
                                "object": {"the": "object"},
                            },
                        }
                    ]
                }
            )
        )
    )

    assert handled_item == {
        "bucket_name": "bucket_foo",
        "event_name": "ObjectCreated:Put",
        "object": {"the": "object"},
    }

    assert s3.get_bucket_notification_configuration(Bucket="bucket_foo")[
        "QueueConfigurations"
    ] == [
        {
            "Events": ["s3:ObjectCreated:*"],
            "Id": "tqp-subscription",
            "QueueArn": "arn:aws:sqs:us-east-1:123456789012:test--foo",
        }
    ]
