from src.ticketshop.core.broker import broker
from pydantic import EmailStr

USER_REGISTERED_QUEUE = "user_registered"


async def publish_user_registered(email: EmailStr) -> None:
    await broker.publish(message=email, queue=USER_REGISTERED_QUEUE)