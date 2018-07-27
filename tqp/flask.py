from .topic_queue_poller import TopicQueuePoller

# -----------------------------------------------------------------------------


class FlaskTopicQueuePoller(TopicQueuePoller):
    def __init__(self, *args, app, **kwargs):
        super().__init__(*args, **kwargs)
        self.app = app
        self.logger = app.logger

    def handle_message(self, *args, **kwargs):
        with self.app.app_context():
            super().handle_message(*args, **kwargs)
