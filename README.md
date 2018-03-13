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


A Flask binding is also provided:

```py
poller = FlaskTopicQueuePoller('my_poller', app=flask_app)
```
