import json

import aio_pika
from aio_pika import connect_robust


class RabbitMQPublisher:
    def __init__(self, url):
        self.url = url
        self.connection = None
        self.channel = None

    async def connect(self):
        self.connection = await connect_robust(url=self.url)

        self.channel = await self.connection.channel()

        await self.channel.declare_queue("review.created", durable=True)

    async def publish_review_created(
        self,
        review_id: int,
        book_id: int,
        rating: int,
    ) -> None:
        if self.channel is None:
            raise RuntimeError("RabbitMQ is not connected")

        event = {
            "event": "review.created",
            "review_id": review_id,
            "book_id": book_id,
            "rating": rating,
        }

        message = aio_pika.Message(
            body=json.dumps(event).encode("utf-8"),
            content_type="application/json",
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
        )

        await self.channel.default_exchange.publish(
            message,
            routing_key="review.created",
        )
        
    async def close(self):
        if self.connection is not None:
            await self.connection.close()
            

        