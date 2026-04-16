from src.ticketshop.core.broker import broker
from pydantic import EmailStr

USER_REGISTERED_QUEUE  = "user_registered"
TICKET_PURCHASED_QUEUE = "ticket_purchased"


async def publish_user_registered(email: EmailStr) -> None:
    await broker.publish(message=email, queue=USER_REGISTERED_QUEUE)


async def publish_ticket_purchased(
    email: str,
    concert_name: str,
    concert_date: str,
    ticket_type_name: str,
    count: int,
    total_price: int,
) -> None:
    await broker.publish(
        message={
            "email": email,
            "concert_name": concert_name,
            "concert_date": concert_date,
            "ticket_type_name": ticket_type_name,
            "count": count,
            "total_price": total_price,
        },
        queue=TICKET_PURCHASED_QUEUE,
    )