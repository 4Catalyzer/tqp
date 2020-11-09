from .topic_queue_poller import TopicQueuePoller


def install():
    from ddtrace import tracer

    base_handle_message = TopicQueuePoller.handle_message

    def _hook_handle_message(self, msg, payload):
        with tracer.trace("tqp.message", self.queue_name, payload["topic"]):
            base_handle_message(self, msg, payload)

    TopicQueuePoller.handle_message = _hook_handle_message
