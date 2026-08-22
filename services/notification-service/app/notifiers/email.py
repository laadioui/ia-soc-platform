from __future__ import annotations

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any

import aiosmtplib
import structlog
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from app.config import settings

logger = structlog.get_logger()

SEVERITY_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}


class EmailNotifier:
    """Email notifier using aiosmtplib for async SMTP delivery."""

    def __init__(self) -> None:
        self._connected = False

    async def connect(self) -> None:
        try:
            self._connected = True
            logger.info(
                "email_notifier_connected",
                host=settings.SMTP_HOST,
                port=settings.SMTP_PORT,
            )
        except Exception as exc:
            logger.error("email_notifier_connect_failed", error=str(exc))
            raise

    async def disconnect(self) -> None:
        self._connected = False
        logger.info("email_notifier_disconnected")

    def _severity_meets_threshold(self, severity: str, threshold: str) -> bool:
        sev = SEVERITY_ORDER.get(severity.lower(), 4)
        thresh = SEVERITY_ORDER.get(threshold.lower(), 2)
        return sev <= thresh

    def _build_incident_email(
        self, payload: dict[str, Any]
    ) -> tuple[str, str, str]:
        incident_id = payload.get("incident_id", payload.get("id", "N/A"))
        title = payload.get("title", "Security Incident")
        severity = payload.get("severity", "unknown").upper()
        status = payload.get("status", "unknown")
        description = payload.get("description", "No description provided")
        assigned_to = payload.get("assigned_to", "Unassigned")
        related_alerts = payload.get("related_alerts", [])
        timestamp = payload.get("timestamp", "N/A")

        subject = f"[SOC] [{severity}] {title} - {incident_id}"

        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; margin: 20px;">
            <div style="background-color: #1a1a2e; color: white; padding: 15px; border-radius: 5px;">
                <h2 style="margin: 0;">SOC Security Alert</h2>
            </div>
            <div style="padding: 20px; border: 1px solid #ddd; border-top: none;">
                <table style="width: 100%; border-collapse: collapse;">
                    <tr>
                        <td style="padding: 8px; font-weight: bold; width: 150px;">Incident ID:</td>
                        <td style="padding: 8px;">{incident_id}</td>
                    </tr>
                    <tr style="background-color: #f9f9f9;">
                        <td style="padding: 8px; font-weight: bold;">Title:</td>
                        <td style="padding: 8px;">{title}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px; font-weight: bold;">Severity:</td>
                        <td style="padding: 8px; color: {'red' if severity in ('CRITICAL', 'HIGH') else 'orange' if severity == 'MEDIUM' else 'green'};">{severity}</td>
                    </tr>
                    <tr style="background-color: #f9f9f9;">
                        <td style="padding: 8px; font-weight: bold;">Status:</td>
                        <td style="padding: 8px;">{status}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px; font-weight: bold;">Assigned To:</td>
                        <td style="padding: 8px;">{assigned_to}</td>
                    </tr>
                    <tr style="background-color: #f9f9f9;">
                        <td style="padding: 8px; font-weight: bold;">Timestamp:</td>
                        <td style="padding: 8px;">{timestamp}</td>
                    </tr>
                </table>
                <div style="margin-top: 20px;">
                    <h3>Description</h3>
                    <p style="padding: 10px; background-color: #f5f5f5; border-radius: 3px;">{description}</p>
                </div>
                {"<div style='margin-top: 20px;'><h3>Related Alerts</h3><ul>" + "".join(f"<li>{alert}</li>" for alert in related_alerts) + "</ul></div>" if related_alerts else ""}
            </div>
            <div style="margin-top: 20px; padding: 10px; background-color: #f0f0f0; font-size: 12px; color: #666;">
                AI SOC Platform - Automated Notification
            </div>
        </body>
        </html>
        """

        plain_body = (
            f"SOC Security Alert\n\n"
            f"Incident ID: {incident_id}\n"
            f"Title: {title}\n"
            f"Severity: {severity}\n"
            f"Status: {status}\n"
            f"Assigned To: {assigned_to}\n"
            f"Timestamp: {timestamp}\n\n"
            f"Description:\n{description}\n\n"
            + (f"Related Alerts: {', '.join(str(a) for a in related_alerts)}\n" if related_alerts else "")
        )

        return subject, html_body, plain_body

    @retry(
        retry=retry_if_exception_type((aiosmtplib.SMTPException, ConnectionError)),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
    )
    async def send_notification(
        self,
        payload: dict[str, Any],
        recipients: list[str] | None = None,
    ) -> bool:
        if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
            logger.warning("email_smtp_not_configured")
            return False

        severity = payload.get("severity", "unknown").lower()
        if not self._severity_meets_threshold(severity, settings.MIN_SEVERITY_FOR_EMAIL):
            logger.debug(
                "email_severity_below_threshold",
                severity=severity,
                threshold=settings.MIN_SEVERITY_FOR_EMAIL,
            )
            return False

        to_addrs = recipients or settings.NOTIFICATION_EMAIL_RECIPIENTS
        if not to_addrs:
            logger.warning("email_no_recipients")
            return False

        subject, html_body, plain_body = self._build_incident_email(payload)

        msg = MIMEMultipart("alternative")
        msg["From"] = f"{settings.SMTP_FROM_NAME} <{settings.SMTP_FROM_EMAIL}>"
        msg["To"] = ", ".join(to_addrs)
        msg["Subject"] = subject
        msg.attach(MIMEText(plain_body, "plain"))
        msg.attach(MIMEText(html_body, "html"))

        try:
            await aiosmtplib.send(
                msg,
                hostname=settings.SMTP_HOST,
                port=settings.SMTP_PORT,
                username=settings.SMTP_USER,
                password=settings.SMTP_PASSWORD,
                use_tls=settings.SMTP_USE_TLS,
                start_tls=settings.SMTP_USE_TLS,
            )
            logger.info(
                "email_sent",
                subject=subject,
                recipients=to_addrs,
                severity=severity,
            )
            return True
        except Exception as exc:
            logger.error(
                "email_send_failed",
                error=str(exc),
                subject=subject,
                recipients=to_addrs,
            )
            raise

    async def health_check(self) -> dict[str, Any]:
        return {
            "status": "configured" if settings.SMTP_USER else "not_configured",
            "host": settings.SMTP_HOST,
            "port": settings.SMTP_PORT,
        }


email_notifier = EmailNotifier()
