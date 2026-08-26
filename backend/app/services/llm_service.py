import logging
import httpx

logger = logging.getLogger(__name__)

OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
OLLAMA_MODEL = "llama3.1:8b"

# Maximum characters per evidence chunk sent to the LLM.
# Keeps token count manageable and avoids Ollama timeouts.
_MAX_CHUNK_CHARS = 500

# Maximum number of evidence chunks to include in the prompt.
_MAX_EVIDENCE_CHUNKS = 3


def _build_evidence_text(evidence: list[dict]) -> str:
    """
    Build a compact, token-efficient evidence block from retrieved chunks.
    Truncates each chunk to _MAX_CHUNK_CHARS and takes at most _MAX_EVIDENCE_CHUNKS.
    """
    # Sort by score (strongest first) and cap at max chunks
    sorted_ev = sorted(evidence, key=lambda x: x.get("score", 0.0), reverse=True)
    top_ev = sorted_ev[:_MAX_EVIDENCE_CHUNKS]

    parts = []
    for i, item in enumerate(top_ev, start=1):
        source = item.get("source") or item.get("title") or "Unknown"
        page = item.get("page", "?")
        text = (item.get("text") or item.get("content") or "").strip()

        # Truncate to keep prompt size under control
        if len(text) > _MAX_CHUNK_CHARS:
            text = text[:_MAX_CHUNK_CHARS] + "…"

        parts.append(f"[{i}] {source} (p.{page}):\n{text}")

    return "\n\n".join(parts)


async def generate_answer(
    question: str,
    evidence: list[dict],
) -> str:
    """
    Generate a grounded answer from local Ollama using retrieved evidence.

    Optimisations vs. original:
    - Evidence truncated to _MAX_CHUNK_CHARS per chunk.
    - Only top-_MAX_EVIDENCE_CHUNKS chunks are sent (sorted by relevance score).
    - Prompt is concise to reduce total token count.
    - Timeout extended to 180 s with a stream=True request so we collect
      chunks incrementally (reduces perceived latency; full answer returned).
    """
    if not evidence:
        return (
            "The available documents do not contain enough "
            "information to answer this question."
        )

    evidence_text = _build_evidence_text(evidence)

    prompt = (
        "You are a precise industrial AI assistant.\n"
        "Answer using ONLY the evidence below. Be concise and factual.\n"
        "If evidence is insufficient, say so clearly.\n\n"
        f"QUESTION: {question}\n\n"
        f"EVIDENCE:\n{evidence_text}\n\n"
        "ANSWER:"
    )

    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": True,
        "options": {
            "temperature": 0.1,
            "num_predict": 512,   # cap output tokens to prevent runaway generation
        },
    }

    try:
        logger.info(
            "Sending request to local Ollama model: %s (evidence chunks: %d)",
            OLLAMA_MODEL,
            min(len(evidence), _MAX_EVIDENCE_CHUNKS),
        )

        answer_parts: list[str] = []

        async with httpx.AsyncClient(timeout=180.0) as client:
            async with client.stream("POST", OLLAMA_URL, json=payload) as resp:
                resp.raise_for_status()
                async for line in resp.aiter_lines():
                    if not line:
                        continue
                    try:
                        import json
                        chunk = json.loads(line)
                        token = chunk.get("response", "")
                        if token:
                            answer_parts.append(token)
                        if chunk.get("done"):
                            break
                    except Exception:
                        continue

        answer = "".join(answer_parts).strip()
        logger.info("Ollama streaming response complete (%d chars).", len(answer))

        if not answer:
            return (
                "The local AI model did not generate an answer "
                "from the available evidence."
            )

        return answer

    except httpx.TimeoutException:
        logger.error("Ollama request timed out after 180 s.")
        raise RuntimeError(
            "The local Ollama model took too long to respond. "
            "Try a lighter model (e.g. llama3.2:3b or phi3:mini)."
        )

    except httpx.HTTPError as exc:
        logger.exception("Ollama HTTP request failed: %s", exc)
        raise RuntimeError(
            "Unable to connect to the local Ollama service. "
            "Make sure Ollama is running: `ollama serve`"
        ) from exc

    except Exception as exc:
        logger.exception("Unexpected Ollama error: %s", exc)
        raise RuntimeError("Local LLM generation failed.") from exc