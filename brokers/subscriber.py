from faststream import FastStream
from faststream.rabbit import RabbitBroker

broker = RabbitBroker()
app = FastStream()

@broker.subscriber("registration")
async def registration_handler(data: str):
    print(data)