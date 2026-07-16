"""Built-in tools the AI can call during a chat turn.

Each tool is defined once here (OpenAI function-calling schema) and
paired with an executor. No external API keys are required for any of
them - calculate and get_current_datetime are fully local, and
web_search uses DuckDuckGo's keyless Instant Answer API.
"""
import ast
import operator
import json
from datetime import datetime, timezone
from typing import Any

import httpx

TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "Evaluate a numeric arithmetic expression, e.g. '12.5 * (3 + 7) / 2'.",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {"type": "string", "description": "A numeric expression using + - * / ** ( )"},
                },
                "required": ["expression"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_current_datetime",
            "description": "Get the current date and time (UTC).",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Search the web for a query and return a short summary of results. Use for current events or facts you're unsure about.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "The search query"},
                },
                "required": ["query"],
            },
        },
    },
]

_ALLOWED_OPS = {
    ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
    ast.Div: operator.truediv, ast.Pow: operator.pow, ast.Mod: operator.mod,
    ast.USub: operator.neg, ast.UAdd: operator.pos,
}


def _safe_eval(node):
    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)):
            return node.value
        raise ValueError("Only numbers are allowed")
    if isinstance(node, ast.BinOp) and type(node.op) in _ALLOWED_OPS:
        return _ALLOWED_OPS[type(node.op)](_safe_eval(node.left), _safe_eval(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _ALLOWED_OPS:
        return _ALLOWED_OPS[type(node.op)](_safe_eval(node.operand))
    raise ValueError("Unsupported expression")


async def calculate(expression: str) -> str:
    try:
        tree = ast.parse(expression, mode="eval")
        result = _safe_eval(tree.body)
        return json.dumps({"result": result})
    except Exception as e:
        return json.dumps({"error": f"Could not evaluate expression: {e}"})


async def get_current_datetime() -> str:
    now = datetime.now(timezone.utc)
    return json.dumps({"utc_datetime": now.isoformat(), "readable": now.strftime("%A, %B %d, %Y %H:%M UTC")})


async def web_search(query: str) -> str:
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                "https://api.duckduckgo.com/",
                params={"q": query, "format": "json", "no_html": 1, "skip_disambig": 1},
            )
            response.raise_for_status()
            data = response.json()

        abstract = data.get("AbstractText", "")
        related = [t.get("Text", "") for t in data.get("RelatedTopics", [])[:3] if t.get("Text")]

        if not abstract and not related:
            return json.dumps({"result": "No direct results found. Answer from general knowledge and say results were limited."})

        return json.dumps({"abstract": abstract, "related": related})
    except Exception as e:
        return json.dumps({"error": f"Web search failed: {e}"})


_EXECUTORS = {
    "calculate": calculate,
    "get_current_datetime": get_current_datetime,
    "web_search": web_search,
}


async def execute_tool(name: str, arguments_json: str) -> str:
    """Run a tool by name with JSON-encoded arguments, returning a JSON string result."""
    executor = _EXECUTORS.get(name)
    if not executor:
        return json.dumps({"error": f"Unknown tool: {name}"})
    try:
        args = json.loads(arguments_json) if arguments_json else {}
    except json.JSONDecodeError:
        return json.dumps({"error": "Invalid tool arguments"})
    return await executor(**args)
