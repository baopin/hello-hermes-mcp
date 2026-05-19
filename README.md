# hello-hermes-mcp 👋

A friendly MCP (Model Context Protocol) server that greets you, tells you about Hermes Agent, and lets you test MCP connectivity.

Built for Hermes Agent's native MCP client — also works with any MCP-compatible client (Claude Desktop, Cursor, etc.).

## Quick Start

### 1. Install with uv

```bash
cd hello-hermes-mcp
uv sync
```

### 2. Test the server

```bash
uv run hello-hermes-mcp
```

The server will start on stdio and wait for MCP client messages.

### 3. Register with Hermes Agent

Add to `~/.hermes/config.yaml`:

```yaml
mcp_servers:
  hello-hermes:
    command: "uv"
    args: ["run", "--directory", "/path/to/hello-hermes-mcp", "hello-hermes-mcp"]
```

Then restart Hermes Agent. The tools `mcp_hello_hermes_greet`, `mcp_hello_hermes_hermes_fact`, and `mcp_hello_hermes_echo_word` will be available.

## Tools

### greet(name, language)

Greet someone in their preferred language.

```json
{
  "name": "Alice",
  "language": "zh"
}
// → "你好, Alice! Welcome to the hello-hermes-mcp server 🎉"
```

Supported languages: en, zh, ja, ko, fr, de, es, it, pt, ru, ar, hi, vi, th, tr

### hermes_fact(topic)

Learn an interesting fact about Hermes Agent.

```json
{ "topic": "mcp" }
// → "Hermes has a built-in native MCP client that connects to MCP servers..."
```

Topics: origin, skills, multi-platform, provider-agnostic, memory, mcp, profiles, cron, gateway, subagents

### echo_word(text, style)

Echo text back with optional formatting — use this to test connectivity.

```json
{
  "text": "hello hermes",
  "style": "reverse"
}
// → "📢 Echo (reverse): semreh olleh"
```

Styles: plain, uppercase, lowercase, reverse, random-case

## Prompts

### welcome

Generate a warm welcome message for someone new to Hermes Agent. Accepts `name` and `language` arguments.

## Resources

| URI Template | Description |
|---|---|
| `hello://greetings/{language}` | Greeting word in a language |
| `hello://facts/{topic}` | Hermes fact for a topic |

## Project Structure

```
hello-hermes-mcp/
├── pyproject.toml              # Project metadata and dependencies
├── README.md                   # This file
└── src/
    └── hello_hermes_mcp/
        └── server.py           # MCP server implementation
```

## Development

```bash
# Install with dev dependencies
uv sync --dev

# Inspect the server with the MCP inspector
uv run mcp dev src/hello_hermes_mcp/server.py
```

## License

MIT
