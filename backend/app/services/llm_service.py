import logging
import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)

OLLAMA_URL = "http://127.0.0.1:11434/api/generate"


async def generate_answer(
    question: str,
    evidence: list[dict],
    model: str | None = None,
) -> str:
    target_model = model or settings.OLLAMA_MODEL

    if not evidence:
        return (
            "The available documents do not contain enough "
            "information to answer this question."
        )

    # Build context from RAG results
    evidence_text = "\n\n".join(
        f"""
Source: {item.get("source", "Unknown")}
Page: {item.get("page", "Unknown")}
Document: {item.get("title", "Unknown")}

Content:
{item.get("text", "")}
""".strip()
        for item in evidence
    )

    # Prompt for grounded generation
    prompt = f"""
You are a secure industrial AI assistant.

Answer the user's question using ONLY the evidence provided below.

RULES:
- Do not use outside knowledge.
- Do not invent facts.
- Do not make assumptions.
- If the evidence is insufficient, clearly say so.
- Give a concise and useful answer.
- Preserve important numbers, dates, equipment names, and events.
- Every factual claim must be supported by the provided evidence.

USER QUESTION:
{question}

EVIDENCE:
{evidence_text}

ANSWER:
"""

    payload = {
        "model": target_model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.1
        }
    }

    try:
        logger.info(
            "Sending request to local Ollama model: %s",
            target_model,
        )

        from app.services.network_logger import record_network_call

        async with httpx.AsyncClient(timeout=120.0) as client:

            response = await client.post(
                OLLAMA_URL,
                json=payload,
            )

            response.raise_for_status()

            data = response.json()

        record_network_call(
            destination=OLLAMA_URL,
            method="POST",
            purpose=f"Local LLM Inference ({target_model})",
            bytes_sent=len(prompt),
            bytes_received=len(data.get("response", "")),
            status_code=response.status_code,
        )

        answer = data.get("response", "").strip()

        logger.info("Ollama response received successfully.")

        if not answer:
            return (
                "The local AI model did not generate an answer "
                "from the available evidence."
            )

        return answer

    except httpx.TimeoutException:
        logger.error("Ollama request timed out.")

        raise RuntimeError(
            "The local Ollama model took too long to generate a response."
        )

    except httpx.HTTPError as exc:
        logger.exception(
            "Ollama HTTP request failed: %s",
            exc,
        )

        raise RuntimeError(
            "Unable to connect to the local Ollama service."
        ) from exc

    except Exception as exc:
        logger.exception(
            "Unexpected Ollama error: %s",
            exc,
        )

        raise RuntimeError(
            "Local LLM generation failed."
        ) from exc