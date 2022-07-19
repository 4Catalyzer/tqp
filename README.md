# TQP

An opinionated library for pub/sub over SQS and SNS

## Topic

To publish on a topic:

```py
topic = Topic('widgets--created')
topic.publish({'id': '123456'})
```

## Topic Queue Poller

To read from the topic:

```py
poller = TopicQueuePoller('my_poller')

@poller.handler('widgets--created')
def process_created_widget(item):
    widget_id = item['id']
    print(f'Widget {widget_id} was created')

poller.start()
```

### S3 notifications

It is also possible to poll for s3 object notifications

```py
@poller.s3_handler('my-bucket-name')
def process_file_created(msg):
    print(msg)
    # {
    #     'event_name': 'ObjectCreated:Put',
    #     'bucket_name': 'bespin-dev-consular21d51f71-11lpitfowdylc',
    #     'object': {
    #         'key': 'genome.fasta',
    #         'size': 124,
    #         'eTag': '5d9d04cd0b9d3b314d9bd622da06ab74',
    #         'sequencer': '005FAD55883A198E97'
    #     },
    # }
```

### Flask

A Flask binding is also provided:

```py
poller = FlaskTopicQueuePoller('my_poller', app=flask_app)
```

When using the Flask poller, you can also specify how to format the logs:

```py
# the argument (optional) is a function that takes the message payload as input and return a message identifier
poller.set_log_formatter(lambda payload: payload["message"].get("id", "<NO ID>"))
```

### Logstash

https://github.com/jquense/logstash-input-tqp

Provides a TQP poller as an LogStash input plugin.

