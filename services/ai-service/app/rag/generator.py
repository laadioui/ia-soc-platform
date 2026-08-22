from __future__ import annotations

import json
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
from app.rag.retriever import retriever

logger = structlog.get_logger()

ANALYSIS_SYSTEM_PROMPT = """You are an expert cybersecurity analyst AI assistant for a Security Operations Center (SOC).
You analyze security events, alerts, and incidents to provide actionable intelligence.
Always respond in JSON format with the following structure:
{
    "analysis": "detailed analysis of the event",
    "severity_assessment": "critical|high|medium|low|info",
    "recommended_actions": ["action1", "action2"],
    "mitre_mapping": {"tactic": "...", "technique": "...", "technique_id": "..."},
    "confidence": 0.0-1.0
}"""

SUMMARIZE_SYSTEM_PROMPT = """You are an expert cybersecurity analyst AI assistant for a Security Operations Center (SOC).
You summarize security reports, alerts, and incident data concisely.
Always respond in JSON format with the following structure:
{
    "summary": "concise summary of the text",
    "key_points": ["point1", "point2", "point3"]
}"""


class LLMGenerator:
    """LLM integration using httpx to call Ollama API for generating security analysis."""

    def __init__(self) -> None:
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=settings.OLLAMA_BASE_URL,
                timeout=httpx.Timeout(120.0, connect=10.0),
                limits=httpx.Limits(max_connections=5, max_keepalive_connections=2),
            )
        return self._client

    @retry(
        retry=retry_if_exception_type((httpx.HTTPError, httpx.TimeoutException)),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
    )
    async def _generate(
        self,
        prompt: str,
        system: str = "",
        temperature: float = 0.3,
        max_tokens: int = 2048,
    ) -> str:
        client = await self._get_client()

        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": settings.OLLAMA_MODEL,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
                "top_p": 0.9,
            },
        }

        response = await client.post("/api/chat", json=payload)
        response.raise_for_status()

        data = response.json()
        content = data.get("message", {}).get("content", "")

        logger.debug(
            "llm_generation_complete",
            model=settings.OLLAMA_MODEL,
            prompt_length=len(prompt),
            response_length=len(content),
        )

        return content

    def _parse_json_response(self, text: str) -> dict[str, Any]:
        text = text.strip()
        if text.startswith("```json"):
            text = text[7:]
        elif text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()

        try:
            return json.loads(text)
        except json.JSONDecodeError:
            start = text.find("{")
            end = text.rfind("}") + 1
            if start != -1 and end > start:
                try:
                    return json.loads(text[start:end])
                except json.JSONDecodeError:
                    pass
            logger.warning("failed_to_parse_llm_json", text=text[:200])
            return {"analysis": text, "severity_assessment": "unknown", "recommended_actions": [], "confidence": 0.0}

    async def analyze_event(
        self,
        event_data: dict[str, Any],
        context: str | None = None,
    ) -> dict[str, Any]:
        event_str = json.dumps(event_data, indent=2, default=str)

        similar_context = await retriever.get_context_for_generation(
            query=event_str, top_k=3
        )

        prompt = f"""Analyze the following security event and provide a detailed security assessment.

## Event Data:
```json
{event_str}
```

## Historical Context (similar past events):
{similar_context}
"""
        if context:
            prompt += f"\n## Additional Context:\n{context}\n"

        prompt += "\nProvide your analysis as a JSON object."

        try:
            response = await self._generate(
                prompt=prompt,
                system=ANALYSIS_SYSTEM_PROMPT,
                temperature=0.2,
            )
            return self._parse_json_response(response)
        except Exception as exc:
            logger.error("llm_analyze_event_error", error=str(exc))
            return {
                "analysis": f"Unable to generate LLM analysis: {exc}",
                "severity_assessment": "unknown",
                "recommended_actions": ["Manual review required"],
                "confidence": 0.0,
            }

    async def summarize(
        self,
        text: str,
        max_length: int | None = None,
    ) -> dict[str, Any]:
        prompt = f"""Summarize the following security-related text.

## Text:
{text}
"""
        if max_length:
            prompt += f"\nProvide a summary in approximately {max_length} words."

        prompt += "\nProvide your summary as a JSON object."

        try:
            response = await self._generate(
                prompt=prompt,
                system=SUMMARIZE_SYSTEM_PROMPT,
                temperature=0.3,
            )
            return self._parse_json_response(response)
        except Exception as exc:
            logger.error("llm_summarize_error", error=str(exc))
            return {
                "summary": f"Unable to generate summary: {exc}",
                "key_points": [],
            }

    async def generate_report(
        self,
        topic: str,
        data: dict[str, Any] | None = None,
    ) -> str:
        prompt = f"Generate a detailed security report on: {topic}"
        if data:
            prompt += f"\n\nData:\n```json\n{json.dumps(data, indent=2, default=str)}\n```"

        try:
            return await self._generate(
                prompt=prompt,
                system="You are an expert cybersecurity report writer. Generate clear, actionable security reports.",
                temperature=0.4,
                max_tokens=4096,
            )
        except Exception as exc:
            logger.error("llm_generate_report_error", error=str(exc))
            return f"Unable to generate report: {exc}"

    async def health_check(self) -> bool:
        try:
            client = await self._get_client()
            response = await client.get("/api/tags")
            return response.status_code == 200
        except Exception as exc:
            logger.warning("llm_health_check_failed", error=str(exc))
            return False
