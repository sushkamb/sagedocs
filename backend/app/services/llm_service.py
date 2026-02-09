from openai import OpenAI
from app.config import settings


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

    def chat(self, system_prompt: str, user_message: str, tools: list = None) -> dict:
        """Send a chat message and get a response. Returns { reply, tool_calls }."""

        if self.provider == "openai":
            return self._chat_openai(system_prompt, user_message, tools)
        elif self.provider == "anthropic":
            return self._chat_anthropic(system_prompt, user_message, tools)

    def _chat_openai(self, system_prompt: str, user_message: str, tools: list = None) -> dict:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ]

        kwargs = {"model": self.model, "messages": messages}
        if tools:
            kwargs["tools"] = tools
            kwargs["tool_choice"] = "auto"

        response = self.client.chat.completions.create(**kwargs)
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

    def _chat_anthropic(self, system_prompt: str, user_message: str, tools: list = None) -> dict:
        kwargs = {
            "model": self.model,
            "max_tokens": 2048,
            "system": system_prompt,
            "messages": [{"role": "user", "content": user_message}],
        }

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

    def get_embedding(self, text: str) -> list[float]:
        """Get embedding vector for text. Uses OpenAI embeddings regardless of chat provider."""
        client = OpenAI(api_key=settings.openai_api_key)
        response = client.embeddings.create(
            model=settings.embedding_model,
            input=text,
        )
        return response.data[0].embedding
