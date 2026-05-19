"""
hello-hermes-mcp — A friendly MCP server that greets you and tells you about Hermes Agent.

Tools:
  - greet(name, language) — Greets someone in their preferred language
  - hermes_fact(topic) — Returns interesting facts about Hermes Agent
  - echo_word(text, style) — Echoes text back with optional formatting
"""

from __future__ import annotations

import json
import random
from typing import Any

from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    GetPromptResult,
    Prompt,
    PromptArgument,
    PromptMessage,
    TextContent,
    Tool,
    ResourceTemplate,
)

# ──────────────────────────────────────────────
#  Resources — static lookup data
# ──────────────────────────────────────────────

GREETINGS = {
    "en": "Hello",
    "zh": "你好",
    "ja": "こんにちは",
    "ko": "안녕하세요",
    "fr": "Bonjour",
    "de": "Hallo",
    "es": "Hola",
    "it": "Ciao",
    "pt": "Olá",
    "ru": "Здравствуйте",
    "ar": "السلام عليكم",
    "hi": "नमस्ते",
    "vi": "Xin chào",
    "th": "สวัสดี",
    "tr": "Merhaba",
}

HERMES_FACTS = [
    {
        "topic": "origin",
        "fact": "Hermes Agent is an open-source AI agent framework by Nous Research, named after the Greek messenger god Hermes.",
    },
    {
        "topic": "skills",
        "fact": "Hermes can 'learn' from experience by saving reusable procedures as skills — markdown files with YAML frontmatter that load into future sessions.",
    },
    {
        "topic": "multi-platform",
        "fact": "The same Hermes Agent instance can run on Telegram, Discord, Slack, WhatsApp, Signal, Matrix, Email, and 10+ other platforms simultaneously.",
    },
    {
        "topic": "provider-agnostic",
        "fact": "Hermes works with 20+ LLM providers including OpenRouter, Anthropic, OpenAI, DeepSeek, Google Gemini, xAI, and local models — switch mid-conversation.",
    },
    {
        "topic": "memory",
        "fact": "Hermes has persistent cross-session memory with pluggable backends (built-in, Honcho, Mem0), so it remembers you between conversations.",
    },
    {
        "topic": "mcp",
        "fact": "Hermes has a built-in native MCP client that connects to MCP servers at startup, discovers their tools, and makes them available as first-class agent tools.",
    },
    {
        "topic": "profiles",
        "fact": "Hermes supports named profiles — independent configs, sessions, skills, and memory — letting you run multiple personalities from the same installation.",
    },
    {
        "topic": "cron",
        "fact": "Hermes has a built-in cron scheduler for recurring tasks — set it to check a website daily, summarize a feed hourly, or any scheduled automation.",
    },
    {
        "topic": "gateway",
        "fact": "The Hermes Gateway lets you run the agent as a background daemon, connecting it to messaging platforms without keeping a terminal open.",
    },
    {
        "topic": "subagents",
        "fact": "Hermes can delegate tasks to parallel subagents via `delegate_task`, each with its own isolated conversation and terminal session.",
    },
]

# ──────────────────────────────────────────────
#  Server instance
# ──────────────────────────────────────────────

app = Server("hello-hermes-mcp")


# ──────────────────────────────────────────────
#  Tools
# ──────────────────────────────────────────────

@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="greet",
            description="Greet someone in their preferred language. Returns a friendly greeting message.",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Name of the person to greet",
                    },
                    "language": {
                        "type": "string",
                        "description": "Language code (en, zh, ja, ko, fr, de, es, it, pt, ru, ar, hi, vi, th, tr)",
                        "default": "en",
                    },
                },
                "required": ["name"],
            },
        ),
        Tool(
            name="hermes_fact",
            description="Learn an interesting fact about Hermes Agent. Optionally filter by topic.",
            inputSchema={
                "type": "object",
                "properties": {
                    "topic": {
                        "type": "string",
                        "description": "Optional topic filter: origin, skills, multi-platform, provider-agnostic, memory, mcp, profiles, cron, gateway, subagents",
                    },
                },
            },
        ),
        Tool(
            name="echo_word",
            description="Echo text back with optional styling — useful for testing MCP connectivity.",
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "Text to echo back",
                    },
                    "style": {
                        "type": "string",
                        "description": "Output style: plain, uppercase, lowercase, reverse, random-case",
                        "default": "plain",
                    },
                },
                "required": ["text"],
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    match name:
        case "greet":
            name_val = arguments["name"]
            lang = arguments.get("language", "en")
            greeting = GREETINGS.get(lang, f"👋 (unsupported language: {lang})")
            return [
                TextContent(
                    type="text",
                    text=f"{greeting}, {name_val}! Welcome to the hello-hermes-mcp server 🎉",
                )
            ]

        case "hermes_fact":
            topic = arguments.get("topic", "").strip().lower()
            if topic:
                matches = [f for f in HERMES_FACTS if f["topic"] == topic]
                if not matches:
                    available = ", ".join(f["topic"] for f in HERMES_FACTS)
                    return [
                        TextContent(
                            type="text",
                            text=f"Unknown topic '{topic}'. Available topics: {available}",
                        )
                    ]
                fact = matches[0]
            else:
                fact = random.choice(HERMES_FACTS)

            return [
                TextContent(
                    type="text",
                    text=f"🤖 **Hermes Fact — {fact['topic']}**\n\n{fact['fact']}",
                )
            ]

        case "echo_word":
            text = arguments["text"]
            style = arguments.get("style", "plain")
            match style:
                case "uppercase":
                    result = text.upper()
                case "lowercase":
                    result = text.lower()
                case "reverse":
                    result = text[::-1]
                case "random-case":
                    result = "".join(
                        c.upper() if random.randint(0, 1) else c.lower() for c in text
                    )
                case _:
                    result = text
            return [
                TextContent(
                    type="text",
                    text=f"📢 Echo ({style}): {result}",
                )
            ]

        case _:
            raise ValueError(f"Unknown tool: {name}")


# ──────────────────────────────────────────────
#  Prompts
# ──────────────────────────────────────────────

@app.list_prompts()
async def list_prompts() -> list[Prompt]:
    return [
        Prompt(
            name="welcome",
            description="Generate a welcome message for someone new to Hermes Agent",
            arguments=[
                PromptArgument(
                    name="name",
                    description="Name of the person being welcomed",
                    required=True,
                ),
                PromptArgument(
                    name="language",
                    description="Language code (default: en)",
                    required=False,
                ),
            ],
        ),
    ]


@app.get_prompt()
async def get_prompt(name: str, arguments: dict[str, str] | None) -> GetPromptResult:
    match name:
        case "welcome":
            name_val = (arguments or {}).get("name", "friend")
            lang = (arguments or {}).get("language", "en")
            greeting = GREETINGS.get(lang, f"Hello")

            return GetPromptResult(
                description=f"Welcome {name_val}",
                messages=[
                    PromptMessage(
                        role="user",
                        content=TextContent(
                            type="text",
                            text=f"{greeting}, {name_val}! 👋\n\n"
                            f"Welcome to Hermes Agent! I'm the hello-hermes-mcp server, "
                            f"and I'm here to help you get started. Try using my tools:\n\n"
                            f"- `greet` — Greet someone\n"
                            f"- `hermes_fact` — Learn about Hermes\n"
                            f"- `echo_word` — Test connectivity\n\n"
                            f"Enjoy your journey with autonomous AI agents! 🚀",
                        ),
                    ),
                ],
            )

        case _:
            raise ValueError(f"Unknown prompt: {name}")


# ──────────────────────────────────────────────
#  Resources (templates)
# ──────────────────────────────────────────────

@app.list_resource_templates()
async def list_resource_templates() -> list[ResourceTemplate]:
    return [
        ResourceTemplate(
            uriTemplate="hello://greetings/{language}",
            name="Greeting in a specific language",
            description="Returns the greeting word in the specified language",
            mimeType="text/plain",
        ),
        ResourceTemplate(
            uriTemplate="hello://facts/{topic}",
            name="Hermes fact by topic",
            description="Returns a Hermes Agent fact for the given topic",
            mimeType="text/plain",
        ),
    ]


@app.read_resource()
async def read_resource(uri: str) -> str:
    if uri.startswith("hello://greetings/"):
        lang = uri.removeprefix("hello://greetings/")
        greeting = GREETINGS.get(lang, f"Unsupported language: {lang}")
        return json.dumps({"language": lang, "greeting": greeting})

    if uri.startswith("hello://facts/"):
        topic = uri.removeprefix("hello://facts/")
        matches = [f for f in HERMES_FACTS if f["topic"] == topic]
        if not matches:
            raise ValueError(f"Unknown topic: {topic}")
        return json.dumps(matches[0])

    raise ValueError(f"Unknown resource: {uri}")


# ──────────────────────────────────────────────
#  Entry point
# ──────────────────────────────────────────────

async def main() -> None:
    """Run the hello-hermes-mcp server over stdio."""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="hello-hermes-mcp",
                server_version="0.1.0",
                capabilities=app.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


if __name__ == "__main__":
    import anyio
    anyio.run(main)
