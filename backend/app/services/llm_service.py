import logging
import httpx

logger = logging.getLogger(__name__)

OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
OLLAMA_MODEL = "llama3.1:8b"


async def generate_answer(
    question: str,
    evidence: list[dict],
) -> str:

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
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.1
        }
    }

    try:
        logger.info(
            "Sending request to local Ollama model: %s",
            OLLAMA_MODEL,
        )

        async with httpx.AsyncClient(timeout=120.0) as client:

            response = await client.post(
                OLLAMA_URL,
                json=payload,
            )

            response.raise_for_status()

            data = response.json()

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