import json
import logging

import newrelic.agent

# -----------------------------------------------------------------------------


def _hook_handle_message(self, raw_msg, payload):
    newrelic.agent.set_transaction_name(payload['handler'].__name__)

    self.handle_message(raw_msg, payload)

    self.send_newrelic_event(payload, success=True)

def _hook_send_newrelic_event(self, payload, success):
    if not self.enable_newrelic:
        return

    newrelic.agent.record_custom_event('TqpEvents', {
        'topic': payload['topic'],
        'queue_name': self.queue_name,
        'success': str(success),
    })

def _hook_handle_error(self, ex, raw_msg, payload):
    self.handle_error(ex, raw_msg, payload)
    self.send_newrelic_event(payload, success=False)


# -----------------------------------------------------------------------------


def install():
    QueuePollerBase._handle_message = newrelic.agent.background_task()(
        QueuePollerBase._handle_message,
    )

    TopicQueuePoller.handle_message = _hook_handle_message
    TopicQueuePoller.send_newrelic_event = _hook_send_newrelic_event
    TopicQueuePoller.handle_error = _hook_handle_error
