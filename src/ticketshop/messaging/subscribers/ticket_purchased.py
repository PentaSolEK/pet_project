import asyncio
import logging
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from faststream.rabbit import RabbitRouter

from src.ticketshop.core.config import settings

router = RabbitRouter()
logger = logging.getLogger("faststream")

PURCHASE_SUBJECT = "Поздравляем с покупкой билетов! 🎫"

PURCHASE_HTML = """\
<html>
<body style="font-family: Arial, sans-serif; background-color: #0f1117; padding: 30px;">
  <div style="max-width: 600px; margin: auto; background: #1a1d27;
              border: 1px solid #2a2f3d; border-radius: 12px; padding: 40px; color: #e8eaef;">
    <h1 style="color: #7c6cf0; margin-top: 0;">🎫 Поздравляем с покупкой!</h1>
    <p style="color: #9aa3b2; font-size: 16px;">
      Ваши билеты успешно оформлены. Ниже информация о вашем заказе.
    </p>

    <div style="background: #12151c; border: 1px solid #2a2f3d; border-radius: 8px;
                padding: 20px; margin: 24px 0;">
      <h2 style="color: #e8eaef; margin-top: 0; font-size: 1.2rem;">📋 Детали заказа</h2>
      <table style="width: 100%; border-collapse: collapse; font-size: 15px;">
        <tr>
          <td style="color: #9aa3b2; padding: 6px 0; width: 40%;">Концерт:</td>
          <td style="color: #e8eaef; font-weight: 600;">{concert_name}</td>
        </tr>
        <tr>
          <td style="color: #9aa3b2; padding: 6px 0;">Дата и время:</td>
          <td style="color: #e8eaef;">{concert_date}</td>
        </tr>
        <tr>
          <td style="color: #9aa3b2; padding: 6px 0;">Тип билета:</td>
          <td style="color: #e8eaef;">{ticket_type_name}</td>
        </tr>
        <tr>
          <td style="color: #9aa3b2; padding: 6px 0;">Количество:</td>
          <td style="color: #e8eaef;">{count} шт.</td>
        </tr>
        <tr style="border-top: 1px solid #2a2f3d;">
          <td style="color: #9aa3b2; padding: 10px 0 6px;">Итого:</td>
          <td style="color: #7c6cf0; font-weight: 700; font-size: 1.1rem;
                     padding-top: 10px;">{total_price} ₽</td>
        </tr>
      </table>
    </div>

    <p style="color: #9aa3b2; font-size: 14px;">
      Предъявите это письмо на входе или покажите QR-код из личного кабинета.
    </p>

    <a href="http://localhost:8000"
       style="display:inline-block; margin-top: 16px; padding: 12px 28px;
              background-color: #7c6cf0; color: white; border-radius: 8px;
              text-decoration: none; font-size: 16px; font-weight: 600;">
      Личный кабинет
    </a>

    <p style="margin-top: 36px; color: #555e72; font-size: 12px;">
      Это письмо сформировано автоматически — отвечать на него не нужно.
    </p>
  </div>
</body>
</html>
"""


def _build_message(to_email: str, data: dict) -> MIMEMultipart:
    msg = MIMEMultipart("alternative")
    msg["Subject"] = PURCHASE_SUBJECT
    msg["From"] = f"{settings.email_from_name} <{settings.email_from or settings.smtp_user}>"
    msg["To"] = to_email

    plain = (
        f"Поздравляем с покупкой!\n\n"
        f"Концерт:      {data['concert_name']}\n"
        f"Дата:         {data['concert_date']}\n"
        f"Тип билета:   {data['ticket_type_name']}\n"
        f"Количество:   {data['count']} шт.\n"
        f"Итого:        {data['total_price']} ₽\n\n"
        f"Предъявите это письмо на входе.\n"
        f"http://localhost:8000\n"
    )
    msg.attach(MIMEText(plain, "plain", "utf-8"))
    msg.attach(MIMEText(PURCHASE_HTML.format(**data), "html", "utf-8"))
    return msg


def _smtp_send_sync(to_email: str, data: dict) -> None:
    msg = _build_message(to_email, data)
    raw = msg.as_string()
    from_addr = settings.smtp_user
    host = settings.smtp_host
    user = settings.smtp_user
    password = settings.smtp_password

    try:
        logger.info("SMTP: trying STARTTLS %s:587 (ticket_purchased)", host)
        with smtplib.SMTP(host, 587, timeout=30) as s:
            s.ehlo()
            s.starttls()
            s.ehlo()
            s.login(user, password)
            s.sendmail(from_addr, [to_email], raw)
        return
    except smtplib.SMTPAuthenticationError:
        raise
    except Exception as exc:
        logger.warning("SMTP STARTTLS/587 failed: %s — trying SSL/465", exc)

    ctx = ssl.create_default_context()
    with smtplib.SMTP_SSL(host, 465, timeout=30, context=ctx) as s:
        s.ehlo()
        s.login(user, password)
        s.sendmail(from_addr, [to_email], raw)


@router.subscriber("ticket_purchased")
async def send_purchase_email(data: dict):
    """
    Отправляет письмо с деталями купленных билетов.
    data: {email, concert_name, concert_date, ticket_type_name, count, total_price}
    """
    to_email = data.get("email")
    if not to_email:
        logger.warning("ticket_purchased: no email in message, skipping")
        return

    if not settings.smtp_user or not settings.smtp_password:
        logger.warning("SMTP credentials not set — skipping purchase email to %s", to_email)
        return

    logger.info("Sending purchase confirmation to %s", to_email)
    try:
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, _smtp_send_sync, to_email, data)
        logger.info("Purchase confirmation sent to %s", to_email)
    except smtplib.SMTPAuthenticationError:
        logger.error("SMTP auth failed — check SMTP_USER / SMTP_PASSWORD in .env")
    except Exception as exc:
        logger.error("Failed to send purchase email to %s: %s", to_email, exc)
