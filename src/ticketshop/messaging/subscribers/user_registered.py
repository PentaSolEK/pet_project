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

WELCOME_SUBJECT = "Добро пожаловать в Ticketmuse! 🎵"

WELCOME_HTML = """\
<html>
<body style="font-family: Arial, sans-serif; background-color: #0f1117; padding: 30px;">
  <div style="max-width: 600px; margin: auto; background: #1a1d27;
              border: 1px solid #2a2f3d; border-radius: 12px; padding: 40px; color: #e8eaef;">
    <h1 style="color: #7c6cf0; margin-top: 0;">🎶 Добро пожаловать в Ticketmuse!</h1>
    <p style="color: #9aa3b2; font-size: 16px;">
      Привет! Мы рады, что ты с нами. Теперь тебе доступны билеты на лучшие концерты.
    </p>
    <p style="font-size: 16px;">
      Твой аккаунт: <strong style="color: #7c6cf0;">{email}</strong>
    </p>
    <a href="http://localhost:8000"
       style="display:inline-block; margin-top:20px; padding:12px 28px;
              background-color:#7c6cf0; color:white; border-radius:8px;
              text-decoration:none; font-size:16px; font-weight:600;">
      Открыть Ticketmuse
    </a>
    <p style="margin-top: 36px; color: #555e72; font-size: 12px;">
      Если вы не регистрировались — просто проигнорируйте это письмо.
    </p>
  </div>
</body>
</html>
"""


def _build_message(to_email: str) -> MIMEMultipart:
    msg = MIMEMultipart("alternative")
    msg["Subject"] = WELCOME_SUBJECT
    msg["From"] = f"{settings.email_from_name} <{settings.email_from or settings.smtp_user}>"
    msg["To"] = to_email
    plain = (
        f"Добро пожаловать в Ticketmuse!\n\n"
        f"Твой аккаунт: {to_email}\n"
        f"Перейти на сайт: http://localhost:8000\n"
    )
    msg.attach(MIMEText(plain, "plain", "utf-8"))
    msg.attach(MIMEText(WELCOME_HTML.format(email=to_email), "html", "utf-8"))
    return msg


def _smtp_send_sync(to_email: str) -> None:
    """
    Синхронная отправка — запускается в thread-пуле через run_in_executor.
    Пробует STARTTLS/587, при неудаче — SSL/465.
    """
    msg = _build_message(to_email)
    raw = msg.as_string()
    from_addr = settings.smtp_user
    host = settings.smtp_host
    user = settings.smtp_user
    password = settings.smtp_password

    # Попытка 1: STARTTLS port 587
    try:
        logger.info("SMTP: trying STARTTLS %s:587", host)
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

    # Попытка 2: SSL port 465
    ctx = ssl.create_default_context()
    with smtplib.SMTP_SSL(host, 465, timeout=30, context=ctx) as s:
        s.ehlo()
        s.login(user, password)
        s.sendmail(from_addr, [to_email], raw)


@router.subscriber("user_registered")
async def send_welcome_email(email: str):
    """
    Отправляет приветственное письмо через SMTP.
    Синхронный smtplib запускается в thread-пуле — event loop не блокируется.
    """
    if not settings.smtp_user or not settings.smtp_password:
        logger.warning("SMTP credentials not set — skipping welcome email to %s", email)
        return

    logger.info("Sending welcome email to %s via SMTP (%s)", email, settings.smtp_host)
    try:
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, _smtp_send_sync, email)
        logger.info("Welcome email successfully sent to %s", email)
    except smtplib.SMTPAuthenticationError:
        logger.error("SMTP auth failed — check SMTP_USER / SMTP_PASSWORD in .env")
    except Exception as exc:
        logger.error("Failed to send welcome email to %s: %s", email, exc)