import newrelic.agent

from . import QueuePollerBase, TopicQueuePoller

# -----------------------------------------------------------------------------


def install():
    QueuePollerBase._handle_message = newrelic.agent.background_task()(
        QueuePollerBase._handle_message,
    )

    base_handle_message = TopicQueuePoller.handle_message
    base_handle_error = TopicQueuePoller.handle_error

    def _hook_handle_message(self, msg, payload):
        newrelic.agent.set_transaction_name(payload['handler'].__name__)

        base_handle_message(self, msg, payload)

        self.send_newrelic_event(payload, success=True)

    def _hook_send_newrelic_event(self, payload, success):
        newrelic.agent.record_custom_event('TqpEvents', {
            'topic': payload['topic'],
            'queue_name': self.queue_name,
            'success': str(success),
        })

    def _hook_handle_error(self, exception, msg, payload):
        base_handle_error(self, exception, msg, payload)
        self.send_newrelic_event(payload, success=False)

    TopicQueuePoller.handle_message = _hook_handle_message
    TopicQueuePoller.send_newrelic_event = _hook_send_newrelic_event
    TopicQueuePoller.handle_error = _hook_handle_error
