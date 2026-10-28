"""Optional LLM integration (Anthropic Messages API). Key is read from env / Streamlit secrets."""
import requests
import config

SYSTEM = ("You are a careful cooking assistant. Give a concise recipe with ingredient quantities, numbered steps, "
          "time, and substitutions. Mention food-safety temperatures where relevant. Respect dietary limits strictly.")


def is_configured() -> bool:
    return bool(config.get_secret("ANTHROPIC_API_KEY"))


def ask(prompt: str, max_tokens: int = 900):
    """Return (text, error). Exactly one of them is None."""
    key = config.get_secret("ANTHROPIC_API_KEY")
    if not key:
        return None, "No ANTHROPIC_API_KEY configured."
    try:
        resp = requests.post("https://api.anthropic.com/v1/messages",
                             headers={"x-api-key": key, "anthropic-version": "2023-06-01", "content-type": "application/json"},
                             json={"model": config.LLM_MODEL, "max_tokens": max_tokens, "system": SYSTEM,
                                   "messages": [{"role": "user", "content": prompt}]}, timeout=45)
        if resp.status_code != 200:
            return None, f"LLM API returned HTTP {resp.status_code}. Check the key and model name."
        text = "".join(b.get("text", "") for b in resp.json().get("content", []))
        return (text or None), (None if text else "LLM returned an empty response.")
    except requests.RequestException as exc:
        return None, f"Could not reach the LLM API: {exc}"
