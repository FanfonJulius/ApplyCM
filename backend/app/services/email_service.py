"""Outgoing email. Brevo's HTTPS API in production, log-only in development.

Render's free tier blocks outbound SMTP ports, so mail goes over HTTPS.
"""

import base64
import logging
from dataclasses import dataclass, field
from typing import List, Optional

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)

BREVO_SEND_URL = "https://api.brevo.com/v3/smtp/email"
_TIMEOUT_SECONDS = 15.0


class EmailNotConfiguredError(RuntimeError):
    """Raised before any work is done when the configured backend cannot send."""


class EmailSendError(RuntimeError):
    pass


@dataclass(frozen=True)
class Attachment:
    filename: str
    content: bytes


@dataclass(frozen=True)
class EmailMessage:
    to: List[str]
    subject: str
    html: str
    text: str
    reply_to: Optional[str] = None
    attachments: List[Attachment] = field(default_factory=list)


def ensure_email_configured() -> None:
    backend = settings.EMAIL_BACKEND.lower()
    if backend == "console":
        return
    if backend != "brevo":
        raise EmailNotConfiguredError(f"Unknown EMAIL_BACKEND '{settings.EMAIL_BACKEND}'.")
    if not settings.BREVO_API_KEY or not settings.EMAIL_FROM_ADDRESS:
        raise EmailNotConfiguredError("Email delivery is not configured (BREVO_API_KEY / EMAIL_FROM_ADDRESS).")


def _apply_redirect(message: EmailMessage) -> EmailMessage:
    redirect = settings.EMAIL_REDIRECT_TO
    if not redirect:
        return message
    original = ", ".join(message.to)
    return EmailMessage(
        to=[redirect],
        subject=f"[TEST - for {original}] {message.subject}",
        html=message.html,
        text=message.text,
        reply_to=message.reply_to,
        attachments=message.attachments,
    )


def _send_brevo(message: EmailMessage) -> None:
    payload = {
        "sender": {"name": settings.EMAIL_FROM_NAME, "email": settings.EMAIL_FROM_ADDRESS},
        "to": [{"email": address} for address in message.to],
        "subject": message.subject,
        "htmlContent": message.html,
        "textContent": message.text,
    }
    if message.reply_to:
        payload["replyTo"] = {"email": message.reply_to}
    if message.attachments:
        payload["attachment"] = [
            {"name": a.filename, "content": base64.b64encode(a.content).decode("ascii")}
            for a in message.attachments
        ]

    try:
        response = httpx.post(
            BREVO_SEND_URL,
            json=payload,
            headers={"api-key": settings.BREVO_API_KEY or "", "accept": "application/json"},
            timeout=_TIMEOUT_SECONDS,
        )
    except httpx.HTTPError as exc:
        raise EmailSendError(f"Could not reach the email provider ({type(exc).__name__}).") from exc

    if response.status_code >= 400:
        try:
            detail = response.json().get("message") or response.text
        except ValueError:
            detail = response.text
        raise EmailSendError(f"Email provider rejected the message ({response.status_code}): {detail[:300]}")


def send_email(message: EmailMessage) -> None:
    """Sends one email or raises EmailSendError / EmailNotConfiguredError."""
    ensure_email_configured()
    message = _apply_redirect(message)
    if settings.EMAIL_BACKEND.lower() == "console":
        logger.info(
            "[email:console] to=%s subject=%r attachments=%s",
            message.to,
            message.subject,
            [f"{a.filename} ({len(a.content)} bytes)" for a in message.attachments],
        )
        return
    _send_brevo(message)
