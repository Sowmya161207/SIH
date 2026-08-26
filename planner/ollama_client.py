"""
ollama_client.py
----------------
Ollama LLM Client for the AI Planner.
Invokes local Ollama (llama3.1:8b) with structured prompt instructions
to generate ExecutionPlan JSON natively.
"""

import logging
import httpx

from .interfaces import BasePlannerLLMClient

logger = logging.getLogger(__name__)

OLLAMA_URL = "http://127.0.0.1:11434/api/generate"


class OllamaPlannerLLMClient(BasePlannerLLMClient):
    """
    Concrete BasePlannerLLMClient calling local Ollama model to produce structured ExecutionPlans.
    """

    def __init__(self, model_name: str = "llama3.1:8b"):
        self.model_name = model_name

    async def complete(self, system_prompt: str, user_prompt: str) -> str:
        prompt = f"""{system_prompt}

USER REQUEST TO PLAN:
{user_prompt}

OUTPUT JSON EXECUTION PLAN ONLY:
"""

        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.0,
                "top_p": 0.1
            }
        }

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(OLLAMA_URL, json=payload)
                response.raise_for_status()
                data = response.json()
                raw_output = data.get("response", "").strip()

            from app.services.network_logger import record_network_call
            record_network_call(
                destination=OLLAMA_URL,
                method="POST",
                purpose=f"AI Planner Execution ({self.model_name})",
                bytes_sent=len(prompt),
                bytes_received=len(raw_output),
                status_code=200,
            )

            return raw_output

        except Exception as exc:
            logger.error("OllamaPlannerLLMClient invocation failed: %s", exc)
            raise RuntimeError(f"Planner LLM communication failed: {exc}") from exc
