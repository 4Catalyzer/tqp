import sentry_sdk
from sentry_sdk.integrations import Integration

from .topic_queue_poller import QueuePollerBase

# -----------------------------------------------------------------------------


class TqpIntegration(Integration):
    identifier = "tqp"

    @staticmethod
    def setup_once():
        base_handle_error = QueuePollerBase.handle_error

        def _hook_handle_error(self, exception, msg, payload):
            base_handle_error(self, exception, msg, payload)

            with sentry_sdk.push_scope() as scope:
                scope.set_extra("payload", payload)
                sentry_sdk.capture_exception(exception)

        QueuePollerBase.handle_error = _hook_handle_error
