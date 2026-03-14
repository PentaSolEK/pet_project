from faststream.rabbit import RabbitBroker
from src.ticketshop.core.config import settings

broker = RabbitBroker(settings.rabbitmq_url)