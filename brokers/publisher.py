from pydantic import EmailStr
from faststream.rabbit import RabbitBroker


async def publish_registration_event(email: EmailStr):
    broker = RabbitBroker()
    await broker.publish(
        message=f"Зарегистрирован новый пользователь: {email}",
        queue="registration",
    )