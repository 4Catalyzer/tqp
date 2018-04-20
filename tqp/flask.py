from .queue_poller import QueuePoller, QueuePollerBase, TopicQueuePoller

# -----------------------------------------------------------------------------


class FlaskMixin(QueuePollerBase):
    def __init__(self, *args, app, **kwargs):
        super().__init__(*args, **kwargs)

        self.app = app
        self.logger = app.logger

    def handle_message(self, msg):
        with self.app.app_context():
            super().handle_message(msg)


# -----------------------------------------------------------------------------


class FlaskQueuePoller(FlaskMixin, QueuePoller):
    pass


class FlaskTopicQueuePoller(FlaskMixin, TopicQueuePoller):
    pass
