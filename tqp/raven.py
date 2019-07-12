from .topic_queue_poller import QueuePollerBase

# -----------------------------------------------------------------------------


def install(client):
    base_handle_error = QueuePollerBase.handle_error

    def _hook_handle_error(self, exception, msg, payload):
        base_handle_error(self, exception, msg, payload)

        client.captureException(extra={"payload": payload})

    QueuePollerBase.handle_error = _hook_handle_error
