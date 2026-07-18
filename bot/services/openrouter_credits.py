"""Залишок кредитів на OpenRouter — для адмінської статистики.

Окремо від LLMClient навмисно: баланс — не LLM-операція, і в абстракцію
провайдерів (де Gemini не має кредитів узагалі) він не лягає.
"""

import httpx

CREDITS_URL = "https://openrouter.ai/api/v1/credits"


async def fetch_remaining_credits(api_key: str, client: httpx.AsyncClient | None = None) -> float | None:
    """Скільки доларів лишилось. None — якщо дізнатись не вдалося.

    Одна спроба без ретраїв: це разовий клік адміна, не критичний шлях.
    """
    try:
        if client is None:
            async with httpx.AsyncClient(timeout=10) as own_client:
                return await _request(own_client, api_key)
        return await _request(client, api_key)
    except (httpx.HTTPError, KeyError, TypeError, ValueError):
        return None


async def _request(client: httpx.AsyncClient, api_key: str) -> float:
    response = await client.get(
        CREDITS_URL, headers={"Authorization": f"Bearer {api_key}"}
    )
    response.raise_for_status()
    data = response.json()["data"]
    return float(data["total_credits"]) - float(data["total_usage"])
