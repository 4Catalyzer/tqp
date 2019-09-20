from flask import _app_ctx_stack as context_stack

from .topic_queue_poller import TopicQueuePoller

# -----------------------------------------------------------------------------

UNDEFINED = object()
CTX_PAYLOAD_KEY = 'payload'

# -----------------------------------------------------------------------------


def _get_tqp_context():
    context = context_stack.top
    if not context:
        raise RuntimeError("working outside of app context")

    if not hasattr(context, 'tqp'):
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
