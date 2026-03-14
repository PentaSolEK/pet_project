import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from faststream.rabbit import RabbitRouter

from src.ticketshop.core.config import settings

router = RabbitRouter()
logger = logging.getLogger("faststream")

WELCOME_SUBJECT = "Добро пожаловать в TicketShop! 🎵"

WELCOME_HTML = """\
<html>
<body style="font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 30px;">
  <div style="max-width: 600px; margin: auto; background: white; border-radius: 10px; padding: 40px;">
    <h1 style="color: #333;">🎶 Добро пожаловать в TicketShop!</h1>
    <p style="color: #555; font-size: 16px;">
      Привет! Мы рады, что ты с нами. Теперь тебе доступны билеты на лучшие концерты.
    </p>
    <p style="color: #555; font-size: 16px;">
      Твой аккаунт: <strong>{email}</strong>
    </p>
    <a href="http://localhost:8000"
       style="display:inline-block; margin-top:20px; padding:12px 24px;
              background-color:#6c63ff; color:white; border-radius:6px;
              text-decoration:none; font-size:16px;">
      Перейти в TicketShop
    </a>
    <p style="margin-top: 30px; color: #aaa; font-size: 12px;">
      Если вы не регистрировались — просто проигнорируйте это письмо.
    </p>
  </div>
</body>
</html>
"""


def _build_message(to_email: str) -> MIMEMultipart:
    msg = MIMEMultipart("alternative")
    msg["Subject"] = WELCOME_SUBJECT
    msg["From"] = settings.email_from or settings.smtp_user or "noreply@ticketshop.com"
    msg["To"] = to_email

    plain = (
        f"Добро пожаловать в TicketShop!\n\n"
        f"Ваш аккаунт: {to_email}\n"
        f"Перейти на сайт: http://localhost:8000\n"
    )
    msg.attach(MIMEText(plain, "plain", "utf-8"))
    msg.attach(MIMEText(WELCOME_HTML.format(email=to_email), "html", "utf-8"))
    return msg


@router.subscriber("user_registered")
async def send_welcome_email(email: str):
    """
    Обработчик события регистрации пользователя:
      - Отправляет HTML-приветствие на почту через SMTP (STARTTLS);
      - Если SMTP не настроен — только логирует.
    """
    if not settings.smtp_user or not settings.smtp_password:
        logger.warning(
            "SMTP credentials not configured (SMTP_USER / SMTP_PASSWORD). "
            "Skipping real email — would have sent welcome email to %s",
            email,
        )
        return

    try:
        msg = _build_message(email)
        logger.info("SMTP debug: host=%s port=%s user=%s password_len=%s",
                    settings.smtp_host, settings.smtp_port,
                    settings.smtp_user,
                    len(settings.smtp_password) if settings.smtp_password else 0,
                    )
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=10) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(settings.smtp_user, settings.smtp_password)
            server.sendmail(msg["From"], [email], msg.as_string())

        logger.info("Welcome email successfully sent to %s", email)

    except smtplib.SMTPAuthenticationError:
        logger.error("SMTP authentication failed. Check SMTP_USER / SMTP_PASSWORD.")
    except smtplib.SMTPException as exc:
        logger.error("Failed to send welcome email to %s: %s", email, exc)
    except OSError as exc:
        logger.error("SMTP connection error (%s:%s): %s", settings.smtp_host, settings.smtp_port, exc)