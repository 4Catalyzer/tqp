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
