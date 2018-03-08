import json

import boto3

# -----------------------------------------------------------------------------


class Topic:
    def __init__(self, topic_name):
        sns = boto3.resource('sns')
        self.topic = sns.create_topic(Name=topic_name)

    def publish(self, message, dump_json=True, **kwargs):
        if dump_json:
            message = json.dumps(message)

        self.topic.publish(Message=message, **kwargs)
