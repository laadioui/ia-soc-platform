from __future__ import annotations

from typing import Any

import httpx
import structlog
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from app.config import settings

logger = structlog.get_logger()

SEVERITY_EMOJI = {
    "critical": "🔴",
    "high": "🟠",
    "medium": "🟡",
    "low": "🟢",
    "info": "ℹ️",
}

SEVERITY_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}


class WebhookNotifier:
    """Webhook notifier for Slack/Discord and custom webhooks."""

    def __init__(self) -> None:
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                timeout=httpx.Timeout(15.0, connect=5.0),
                limits=httpx.Limits(max_connections=10, max_keepalive_connections=5),
            )
        return self._client

    async def close(self) -> None:
        if self._client is not None and not self._client.is_closed:
            await self._client.aclose()
            logger.info("webhook_client_closed")

    def _severity_meets_threshold(self, severity: str, threshold: str) -> bool:
        sev = SEVERITY_ORDER.get(severity.lower(), 4)
        thresh = SEVERITY_ORDER.get(threshold.lower(), 2)
        return sev <= thresh

    def _build_slack_payload(self, payload: dict[str, Any]) -> dict[str, Any]:
        incident_id = payload.get("incident_id", payload.get("id", "N/A"))
        title = payload.get("title", "Security Incident")
        severity = payload.get("severity", "unknown").upper()
        status = payload.get("status", "unknown")
        description = payload.get("description", "No description provided")
        assigned_to = payload.get("assigned_to", "Unassigned")
        timestamp = payload.get("timestamp", "N/A")
        emoji = SEVERITY_EMOJI.get(severity.lower(), "❓")

        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"{emoji} SOC Security Alert - {severity}",
                },
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*Incident ID:*\n{incident_id}"},
                    {"type": "mrkdwn", "text": f"*Title:*\n{title}"},
                    {"type": "mrkdwn", "text": f"*Severity:*\n{severity}"},
                    {"type": "mrkdwn", "text": f"*Status:*\n{status}"},
                    {"type": "mrkdwn", "text": f"*Assigned To:*\n{assigned_to}"},
                    {"type": "mrkdwn", "text": f"*Timestamp:*\n{timestamp}"},
                ],
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Description:*\n{description[:2000]}",
                },
            },
            {"type": "divider"},
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": "AI SOC Platform - Automated Notification",
                    }
                ],
            },
        ]

        return {"blocks": blocks, "text": f"SOC Alert: [{severity}] {title} - {incident_id}"}

    def _build_discord_payload(self, payload: dict[str, Any]) -> dict[str, Any]:
        incident_id = payload.get("incident_id", payload.get("id", "N/A"))
        title = payload.get("title", "Security Incident")
        severity = payload.get("severity", "unknown").upper()
        status = payload.get("status", "unknown")
        description = payload.get("description", "No description provided")
        assigned_to = payload.get("assigned_to", "Unassigned")
        timestamp = payload.get("timestamp", "N/A")
        emoji = SEVERITY_EMOJI.get(severity.lower(), "❓")

        color_map = {
            "critical": 0xFF0000,
            "high": 0xFF8C00,
            "medium": 0xFFD700,
            "low": 0x00FF00,
            "info": 0x0099FF,
        }
        color = color_map.get(severity.lower(), 0x808080)

        embed = {
            "title": f"{emoji} SOC Security Alert - {severity}",
            "description": description[:4000],
            "color": color,
            "fields": [
                {"name": "Incident ID", "value": str(incident_id), "inline": True},
                {"name": "Title", "value": title, "inline": True},
                {"name": "Severity", "value": severity, "inline": True},
                {"name": "Status", "value": status, "inline": True},
                {"name": "Assigned To", "value": assigned_to, "inline": True},
                {"name": "Timestamp", "value": str(timestamp), "inline": True},
            ],
            "footer": {"text": "AI SOC Platform - Automated Notification"},
        }

        return {"embeds": [embed], "content": f"{emoji} SOC Alert: [{severity}] {title}"}

    def _build_custom_payload(self, payload: dict[str, Any]) -> dict[str, Any]:
        return {
            "event_type": "security_incident",
            "source": "ai-soc-platform",
            **payload,
        }

    @retry(
        retry=retry_if_exception_type((httpx.HTTPError, httpx.TimeoutException)),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
    )
    async def _send_webhook(self, url: str, data: dict[str, Any]) -> bool:
        client = await self._get_client()
        response = await client.post(url, json=data)
        response.raise_for_status()
        return True

    async def send_slack_notification(self, payload: dict[str, Any]) -> bool:
        if not settings.SLACK_WEBHOOK_URL:
            logger.debug("slack_webhook_not_configured")
            return False

        severity = payload.get("severity", "unknown").lower()
        if not self._severity_meets_threshold(severity, settings.MIN_SEVERITY_FOR_WEBHOOK):
            logger.debug(
                "slack_severity_below_threshold",
                severity=severity,
                threshold=settings.MIN_SEVERITY_FOR_WEBHOOK,
            )
            return False

        slack_payload = self._build_slack_payload(payload)

        try:
            await self._send_webhook(settings.SLACK_WEBHOOK_URL, slack_payload)
            logger.info(
                "slack_notification_sent",
                severity=severity,
                title=payload.get("title", "N/A"),
            )
            return True
        except Exception as exc:
            logger.error("slack_notification_failed", error=str(exc))
            return False

    async def send_discord_notification(self, payload: dict[str, Any]) -> bool:
        if not settings.DISCORD_WEBHOOK_URL:
            logger.debug("discord_webhook_not_configured")
            return False

        severity = payload.get("severity", "unknown").lower()
        if not self._severity_meets_threshold(severity, settings.MIN_SEVERITY_FOR_WEBHOOK):
            logger.debug(
                "discord_severity_below_threshold",
                severity=severity,
                threshold=settings.MIN_SEVERITY_FOR_WEBHOOK,
            )
            return False

        discord_payload = self._build_discord_payload(payload)

        try:
            await self._send_webhook(settings.DISCORD_WEBHOOK_URL, discord_payload)
            logger.info(
                "discord_notification_sent",
                severity=severity,
                title=payload.get("title", "N/A"),
            )
            return True
        except Exception as exc:
            logger.error("discord_notification_failed", error=str(exc))
            return False

    async def send_custom_webhook_notification(self, payload: dict[str, Any]) -> list[bool]:
        results = []
        webhook_payload = self._build_custom_payload(payload)

        for url in settings.CUSTOM_WEBHOOK_URLS:
            if not url:
                continue
            try:
                await self._send_webhook(url, webhook_payload)
                results.append(True)
                logger.info("custom_webhook_sent", url=url)
            except Exception as exc:
                logger.error("custom_webhook_failed", url=url, error=str(exc))
                results.append(False)

        return results

    async def send_all_notifications(self, payload: dict[str, Any]) -> dict[str, Any]:
        results: dict[str, Any] = {}

        results["slack"] = await self.send_slack_notification(payload)
        results["discord"] = await self.send_discord_notification(payload)
        results["custom_webhooks"] = await self.send_custom_webhook_notification(payload)

        logger.info(
            "notifications_dispatched",
            incident_id=payload.get("incident_id", payload.get("id")),
            results=results,
        )

        return results

    async def health_check(self) -> dict[str, Any]:
        return {
            "status": "healthy",
            "slack_configured": bool(settings.SLACK_WEBHOOK_URL),
            "discord_configured": bool(settings.DISCORD_WEBHOOK_URL),
            "custom_webhooks_count": len([u for u in settings.CUSTOM_WEBHOOK_URLS if u]),
        }


webhook_notifier = WebhookNotifier()
