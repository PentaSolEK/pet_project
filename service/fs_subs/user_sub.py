import logging

from faststream.rabbit import RabbitRouter

router = RabbitRouter()
logger = logging.getLogger("faststream")


@router.subscriber("user_registered")
async def send_welcome_email(email: str):
    """
    Функция обработки регистрации пользователя:
        - Присылает приветственное сообщение пользователю;
        - Пишет в логах о том, что сообщение отправлено
    :param email:
    :return:
    """
    logger.info(
        f"Sent welcome msg to {email}"
    )