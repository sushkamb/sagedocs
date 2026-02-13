import base64
import logging

from openai import OpenAI, BadRequestError
from app.config import settings

logger = logging.getLogger(__name__)


class LLMService:
    """Abstraction over LLM providers (OpenAI, Anthropic)."""

    def __init__(self, provider: str = None, api_key: str = None, model: str = None):
        self.provider = provider or settings.llm_provider
        self.model = model or settings.llm_model

        if self.provider == "openai":
            self.client = OpenAI(api_key=api_key or settings.openai_api_key)
        elif self.provider == "anthropic":
            import anthropic
            self.client = anthropic.Anthropic(api_key=api_key or settings.anthropic_api_key)

    def chat(self, system_prompt: str, user_message: str, tools: list = None,
             temperature: float = None, max_tokens: int = 2048) -> dict:
        """Send a chat message and get a response. Returns { reply, tool_calls }."""

        if self.provider == "openai":
            return self._chat_openai(system_prompt, user_message, tools, temperature, max_tokens)
        elif self.provider == "anthropic":
            return self._chat_anthropic(system_prompt, user_message, tools, temperature, max_tokens)

    def _chat_openai(self, system_prompt: str, user_message: str, tools: list = None,
                      temperature: float = None, max_tokens: int = 2048) -> dict:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ]

        kwargs = {"model": self.model, "messages": messages}
        if temperature is not None:
            kwargs["temperature"] = temperature
        if tools:
            kwargs["tools"] = tools
            kwargs["tool_choice"] = "auto"

        try:
            response = self.client.chat.completions.create(**kwargs)
        except BadRequestError as e:
            # Some models don't support temperature — retry without it
            if "temperature" in str(e) and "temperature" in kwargs:
                logger.info(f"Model {self.model} doesn't support temperature, retrying without it")
                del kwargs["temperature"]
                response = self.client.chat.completions.create(**kwargs)
            else:
                raise
        choice = response.choices[0]

        result = {"reply": "", "tool_calls": []}

        if choice.message.content:
            result["reply"] = choice.message.content

        if choice.message.tool_calls:
            result["tool_calls"] = [
                {
                    "name": tc.function.name,
                    "arguments": tc.function.arguments,
                }
                for tc in choice.message.tool_calls
            ]

        return result

    def _chat_anthropic(self, system_prompt: str, user_message: str, tools: list = None,
                         temperature: float = None, max_tokens: int = 2048) -> dict:
        kwargs = {
            "model": self.model,
            "max_tokens": max_tokens,
            "system": system_prompt,
            "messages": [{"role": "user", "content": user_message}],
        }

        if temperature is not None:
            kwargs["temperature"] = temperature
        if tools:
            kwargs["tools"] = self._convert_tools_to_anthropic(tools)

        response = self.client.messages.create(**kwargs)

        result = {"reply": "", "tool_calls": []}

        for block in response.content:
            if block.type == "text":
                result["reply"] += block.text
            elif block.type == "tool_use":
                result["tool_calls"].append(
                    {"name": block.name, "arguments": block.input}
                )

        return result

    def _convert_tools_to_anthropic(self, openai_tools: list) -> list:
        """Convert OpenAI tool format to Anthropic tool format."""
        anthropic_tools = []
        for tool in openai_tools:
            func = tool["function"]
            anthropic_tools.append({
                "name": func["name"],
                "description": func["description"],
                "input_schema": func["parameters"],
            })
        return anthropic_tools

    def describe_image(self, image_bytes: bytes, context: str = "") -> str:
        """Describe a screenshot/image using GPT-5.2 vision. Returns text description."""
        b64 = base64.b64encode(image_bytes).decode("utf-8")
        data_url = f"data:image/png;base64,{b64}"

        prompt = (
            "You are describing a screenshot from a software help document. "
            "Describe what the screenshot shows in detail: UI elements, buttons, "
            "form fields, labels, menus, highlighted areas, and any visible text. "
            "Be specific about layout and element positions (top-right, sidebar, etc). "
            "Keep the description to 2-4 sentences."
        )
        if context:
            prompt += f"\n\nSurrounding text context: {context}"

        try:
            client = OpenAI(api_key=settings.openai_api_key)
            response = client.chat.completions.create(
                model=settings.llm_model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {"type": "image_url", "image_url": {"url": data_url}},
                        ],
                    }
                ],
                max_tokens=300,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"[Image could not be described: {e}]"

    def get_embedding(self, text: str) -> list[float]:
        """Get embedding vector for text. Uses OpenAI embeddings regardless of chat provider."""
        client = OpenAI(api_key=settings.openai_api_key)
        response = client.embeddings.create(
            model=settings.embedding_model,
            input=text,
        )
        return response.data[0].embedding
