import pika
from config import _logger, access_secret_version


class QueuePublisherClient(object):
    def __init__(self, queue, request):
        self.queue = queue
        self.request = request
        res = access_secret_version()
        credentials = pika.PlainCredentials(res['pika_username'], res['pika_secret'])
        self.parameters = pika.ConnectionParameters(host=res['pika_host'], credentials=credentials)

    def on_response_connected(self):
        _logger.info("connecting to a broker")
        connection = pika.BlockingConnection(self.parameters)
        channel = connection.channel()
        _logger.info("declaring queue {}".format(self.queue))
        channel.queue_declare(queue=self.queue, durable=True)

        # We need to bind this channel to an exchange, that will be used to transfer
        # messages from our delay queue.
        channel.queue_bind(exchange='amq.direct',
                           queue=self.queue)

        # Create our delay channel.
        delay_channel = connection.channel()
        # delay_channel.confirm_delivery()

        # This is where we declare the delay, and routing for our delay channel.
        delay_channel.queue_declare(queue='delay_queue', durable=True, arguments={
            'x-message-ttl': 5000,  # Delay until the message is transferred in milliseconds.
            'x-dead-letter-exchange': 'amq.direct',  # Exchange used to transfer the message from A to B.
            'x-dead-letter-routing-key': self.queue  # Name of the queue we want the message transferred to.
        })

        _logger.info("Publishing Message to ...({})".format(self.queue))
        delay_channel.basic_publish(exchange='',
                                    routing_key='delay_queue',
                                    body=str(self.request),
                                    properties=pika.BasicProperties(delivery_mode=2))

        _logger.info("Published Message...({})".format(self.request))
        connection.close()
        _logger.info("Connection closed...({})".format(self.queue))
