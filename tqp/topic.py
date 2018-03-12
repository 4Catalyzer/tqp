import json

import boto3

# -----------------------------------------------------------------------------


class Topic:
    def __init__(self, topic_name):
        self.topic_name = topic_name
        self._topic = None

    @property
    def topic(self):
        if self._topic is not None:
            return self._topic

        sns = boto3.resource('sns')
        self._topic = sns.create_topic(Name=self.topic_name)
        return self._topic

    def publish(self, message, dump_json=True, **kwargs):
        if dump_json:
            message = json.dumps(message)

        self.topic.publish(Message=message, **kwargs)
