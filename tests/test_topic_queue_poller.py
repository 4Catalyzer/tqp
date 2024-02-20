import boto3
import json
import moto
import time
from moto import mock_aws
from threading import Thread
from unittest.mock import Mock

from tqp.topic_queue_poller import TopicQueuePoller, create_queue

# -----------------------------------------------------------------------------


@mock_aws
def test_create_queue():
    create_queue("foo", tags={"my": "tag"})

    sqs_client = boto3.client("sqs", region_name="us-east-1")
    queue = sqs_client.create_queue(QueueName="foo")
    dlq = sqs_client.create_queue(QueueName="foo-dead-letter")

    assert sqs_client.list_queue_tags(QueueUrl=queue["QueueUrl"])["Tags"] == {
        "tqp": "true",
        "dlq": "false",
        "my": "tag",
    }
    assert sqs_client.list_queue_tags(QueueUrl=dlq["QueueUrl"])["Tags"] == {
        "tqp": "true",
        "dlq": "true",
        "my": "tag",
    }
    redrive_policy_resp = sqs_client.get_queue_attributes(
        QueueUrl=queue["QueueUrl"], AttributeNames=["RedrivePolicy"]
    )
    assert json.loads(redrive_policy_resp["Attributes"]["RedrivePolicy"]) == {
        "maxReceiveCount": 5,
        "deadLetterTargetArn": f"arn:aws:sqs:us-east-1:{moto.core.DEFAULT_ACCOUNT_ID}:foo-dead-letter",
    }


@mock_aws
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
    time.sleep(0.5)

    boto3.client("sns").publish(
        TopicArn="arn:aws:sns:us-east-1:123456789012:test--my_event",
        Message='{"bar": "baz"}',
    )

    # making sure message is processed
    time.sleep(0.5)

    assert handled_item == {"bar": "baz"}


@mock_aws
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
