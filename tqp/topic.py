import json

import boto3

# -----------------------------------------------------------------------------


class Topic:
    def __init__(self, topic_name, json_encoder=None):
        self.json_encoder = json_encoder
        self.topic_name = topic_name
        self._topic = None

    @property
    def topic(self):
        if self._topic is not None:
            return self._topic

        sns = boto3.resource('sns')
        self._topic = sns.create_topic(Name=self.topic_name)
        return self._topic

    def publish(self, message, json_encoder=None, **kwargs):
        if not isinstance(message, str):
            message = json.dumps(message, cls=json_encoder or self.json_encoder)

        self.topic.publish(Message=message, **kwargs)
