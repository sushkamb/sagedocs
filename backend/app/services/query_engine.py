import json
import os
import yaml
import httpx
from pathlib import Path

from app.config import settings
from app.services.llm_service import LLMService


class QueryEngine:
    """Data query engine using LLM function calling against host app APIs."""

    def __init__(self):
        self.llm = LLMService()
        self.tool_registries = {}
        self._load_all_registries()

    def _load_all_registries(self):
        """Load all tool registry YAML files from the tools directory."""
        tools_dir = Path(__file__).parent.parent.parent / "tools"
        if not tools_dir.exists():
            return

        for yaml_file in tools_dir.glob("*.yaml"):
            tenant = yaml_file.stem
            with open(yaml_file, "r") as f:
                registry = yaml.safe_load(f)
            self.tool_registries[tenant] = registry

    def _get_openai_tools(self, tenant: str) -> list[dict]:
        """Convert tool registry to OpenAI function calling format."""
        registry = self.tool_registries.get(tenant)
        if not registry:
            return []

        openai_tools = []
        for tool in registry.get("tools", []):
            properties = {}
            required = []
            for param in tool.get("parameters", []):
                prop = {"type": param["type"], "description": param["description"]}
                if "enum" in param:
                    prop["enum"] = param["enum"]
                properties[param["name"]] = prop
                if param.get("required", False):
                    required.append(param["name"])

            openai_tools.append({
                "type": "function",
                "function": {
                    "name": tool["name"],
                    "description": tool["description"],
                    "parameters": {
                        "type": "object",
                        "properties": properties,
                        "required": required,
                    },
                },
            })

        return openai_tools

    def _load_tenant_config(self, tenant: str) -> dict:
        config_path = os.path.join(
            os.path.dirname(__file__), "..", "..", "data", "tenants", f"{tenant}.json"
        )
        if os.path.exists(config_path):
            with open(config_path, "r") as f:
                return json.load(f)
        return {}

    def _get_tool_config(self, tenant: str, tool_name: str) -> dict:
        """Get a specific tool's config from the registry."""
        registry = self.tool_registries.get(tenant, {})
        for tool in registry.get("tools", []):
            if tool["name"] == tool_name:
                return tool
        return None

    async def query(
        self,
        tenant: str,
        question: str,
        account_number: str,
        token: str,
        base_url: str = None,
    ) -> dict:
        """Answer a data question using function calling."""

        tools = self._get_openai_tools(tenant)
        if not tools:
            return {
                "reply": "Data queries are not configured for this application yet.",
                "sources": [],
            }

        tenant_config = self._load_tenant_config(tenant)
        tenant_display = tenant_config.get("display_name", tenant)
        temperature = tenant_config.get("data_temperature") or settings.data_temperature

        registry = self.tool_registries.get(tenant, {})
        base_url = base_url or registry.get("base_url", "")

        system_prompt = (
            f"You are SageDocs, a data assistant for {tenant_display}. "
            "You help users retrieve and understand information from their application.\n\n"
            "## Instructions\n"
            "- Use the available tools to answer the user's question. Call multiple tools if needed.\n"
            "- Format numbers with appropriate separators (e.g., 1,234 not 1234).\n"
            "- Format currency values with $ and two decimal places.\n"
            "- Present data clearly: use tables for comparisons, lists for enumerations.\n"
            "- If a question cannot be answered with the available tools, explain what data "
            "is available and suggest how the user might rephrase their question."
        )

        # First call — LLM decides which tool(s) to use
        result = self.llm.chat(system_prompt, question, tools, temperature=temperature)

        if not result["tool_calls"]:
            return {"reply": result["reply"], "sources": []}

        # Execute tool calls against the host app API
        tool_results = []
        for tool_call in result["tool_calls"]:
            tool_config = self._get_tool_config(tenant, tool_call["name"])
            if not tool_config:
                continue

            args = json.loads(tool_call["arguments"]) if isinstance(tool_call["arguments"], str) else tool_call["arguments"]

            # Call the host app API
            api_result = await self._call_api(
                base_url=base_url,
                endpoint=tool_config["endpoint"],
                method=tool_config.get("method", "GET"),
                params=args,
                account_number=account_number,
                token=token,
            )
            tool_results.append({
                "tool": tool_call["name"],
                "result": api_result,
            })

        # Second call — LLM formats the results into a natural language response
        followup_prompt = (
            f"The user asked: {question}\n\n"
            f"Here are the results from the data queries:\n"
            f"{json.dumps(tool_results, indent=2, default=str)}\n\n"
            "Please provide a clear, concise answer based on these results."
        )

        final_result = self.llm.chat(system_prompt, followup_prompt, temperature=temperature)

        return {"reply": final_result["reply"], "sources": []}

    async def _call_api(
        self,
        base_url: str,
        endpoint: str,
        method: str,
        params: dict,
        account_number: str,
        token: str,
    ) -> dict:
        """Call the host application's API."""
        url = f"{base_url}{endpoint}"
        headers = {
            "Authorization": f"Bearer {token}",
            "X-Account-Number": account_number,
        }

        async with httpx.AsyncClient(timeout=120.0, verify=False) as client:
            if method.upper() == "GET":
                response = await client.get(url, params=params, headers=headers)
            elif method.upper() == "POST":
                response = await client.post(url, json=params, headers=headers)
            else:
                return {"error": f"Unsupported method: {method}"}

            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"API returned status {response.status_code}"}
