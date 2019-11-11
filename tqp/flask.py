import logging

import flask
from flask import _app_ctx_stack as context_stack

from .topic_queue_poller import TopicQueuePoller

# -----------------------------------------------------------------------------

UNDEFINED = object()
CTX_PAYLOAD_KEY = "payload"

# -----------------------------------------------------------------------------


def _get_tqp_context():
    context = context_stack.top
    if not context:
        raise RuntimeError("working outside of app context")

    if not hasattr(context, "tqp"):
        context.tqp = {}

    return context.tqp


def get_ctx_payload():
    tqp_context = _get_tqp_context()

    if CTX_PAYLOAD_KEY not in tqp_context:
        raise RuntimeError("working outside of poller handler")

    return tqp_context[CTX_PAYLOAD_KEY]


# -----------------------------------------------------------------------------


class FlaskTopicQueuePoller(TopicQueuePoller):
    def __init__(self, *args, app, **kwargs):
        super().__init__(*args, **kwargs)
        self.app = app
        self.logger = app.logger

    def handle_message(self, msg, payload):
        with self.app.app_context():
            _get_tqp_context()[CTX_PAYLOAD_KEY] = payload
            super().handle_message(msg, payload)

    def set_log_formatter(self, get_message_id: None):
        class PollerFormatter(logging.Formatter):
            def format(self, record):
                record.topic_name = None
                record.message_id = None

                if flask.has_app_context():
                    payload = get_ctx_payload()
                    record.topic_name = payload["topic"]
                    if get_message_id:
                        record.message_id = get_message_id(payload)

                return super().format(record)

        flask.logging.default_handler.setFormatter(
            PollerFormatter(
                "[%(asctime)s] %(levelname)s in %(module)s %(topic_name)s(%(message_id)s): %(message)s",  # noqa E501
            ),
        )
