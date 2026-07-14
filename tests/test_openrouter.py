"""OpenRouterClient: збірка повідомлення і параметрів без реальних викликів API."""

from types import SimpleNamespace

from bot.services.llm.openrouter import OpenRouterClient, _file_part, _text_part


class StubCompletions:
    def __init__(self, content: str):
        self.calls: list[dict] = []
        self._content = content

    async def create(self, **kwargs):
        self.calls.append(kwargs)
        message = SimpleNamespace(content=self._content)
        return SimpleNamespace(choices=[SimpleNamespace(message=message)])


def _client_with_stub(content: str) -> tuple[OpenRouterClient, StubCompletions]:
    client = OpenRouterClient(api_key="test", model="google/gemini-3.5-flash")
    stub = StubCompletions(content)
    client._client = SimpleNamespace(chat=SimpleNamespace(completions=stub))
    return client, stub


def test_file_part_pdf_and_image():
    pdf = _file_part(b"%PDF", "application/pdf")
    assert pdf["type"] == "file"
    assert pdf["file"]["file_data"].startswith("data:application/pdf;base64,")
    image = _file_part(b"\xff\xd8", "image/jpeg")
    assert image["type"] == "image_url"
    assert image["image_url"]["url"].startswith("data:image/jpeg;base64,")


async def test_extract_recipe_builds_multimodal_message():
    client, stub = _client_with_stub('{"is_recipe": true, "title": "Борщ"}')
    result = await client.extract_recipe(
        "текст рецепта",
        [(b"\xff\xd8", "image/jpeg"), (b"%PDF", "application/pdf")],
    )
    assert result.is_recipe and result.title == "Борщ"

    (call,) = stub.calls
    (message,) = call["messages"]
    assert message["role"] == "user"
    assert [part["type"] for part in message["content"]] == [
        "text",
        "text",
        "image_url",
        "file",
    ]
    # PDF читає сама модель — без платного OCR від OpenRouter
    assert call["extra_body"]["plugins"] == [
        {"id": "file-parser", "pdf": {"engine": "native"}}
    ]
    schema = call["response_format"]["json_schema"]
    assert schema["name"] == "RecipeExtraction" and schema["strict"] is True


async def test_route_query_has_no_pdf_plugins():
    client, stub = _client_with_stub('{"intent": "find_dish"}')
    result = await client.route_query("що на вечерю?")
    assert result.intent == "find_dish"
    (call,) = stub.calls
    assert "plugins" not in call["extra_body"]
    assert _text_part("що на вечерю?")["type"] == "text"
