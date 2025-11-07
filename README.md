## Simple Agent

A tiny, KISS-friendly command line agent that can talk to either OpenAI's ChatGPT API or Google's Gemini API. The agent supports a pluggable backend, a light tool loop, and environment-driven configuration.

### Make targets (uvx-powered)

The repo ships with a lightweight `Makefile` wired to [`uvx`](https://docs.astral.sh/uv/guides/tools/) for reproducible tooling:

- `make venv` – create a local virtual environment at `env/` (activate with `source env/bin/activate`).
- `make install` – install dependencies (uses `env/bin/python` if `make venv` ran, otherwise falls back to `uvx python`).
- `make run PROMPT="hello"` – run the agent with the provided prompt.
- `make tools` – list the currently wired tools.
- `make lint` – run Ruff via `uvx` (no local install required).

### Quick start

1. Create a virtual environment for Python 3.11+ and install the dependencies:
   ```bash
   make install
   ```
2. Copy `.env.example` to `.env` and fill in the API keys you plan to use.
3. Run the agent:
   ```bash
   make run PROMPT="Summarize the latest message."
   ```

### Configuration

All settings live in `.env` (loaded with `python-dotenv`):

| Variable | Description |
| --- | --- |
| `LLM_BACKEND` | `chatgpt` or `gemini`. |
| `OPENAI_API_KEY` | Required for the ChatGPT backend. |
| `OPENAI_MODEL` | Defaults to `gpt-4o-mini`. |
| `GEMINI_API_KEY` | Required for the Gemini backend. |
| `GEMINI_MODEL` | Defaults to `gemini-1.5-flash`. |
| `AGENT_SYSTEM_PROMPT` | Optional custom system prompt. |
| `REQUEST_TIMEOUT` | Request timeout in seconds (default `30`). |

The repository already contains `.env.example` with placeholders for these values.

### CLI options

```
python main.py --help
```

- `prompt` (positional): user message. If missing, you will be prompted in the terminal.
- `--backend`: override the backend without touching `.env`.
- `--max-turns`: maximum number of tool iterations.
- `--no-tools`: disable tool use.
- `--list-tools`: inspect available tools.

### Tools

Tools live under `simple_agent/tools` and implement a tiny interface (`name`, `description`, `run`). Two simple defaults ship with the CLI:

- `time`: returns the current UTC timestamp.
- `calculator`: evaluates small arithmetic expressions safely.

Adding new tools only requires dropping a module next to the others and including it in `load_default_tools()`.

### Extending the agent

- To add more model providers, create a new backend in `simple_agent/backends` that implements `LLMBackend`.
- Swap in custom tools by editing `load_default_tools()` or wiring your own list in `main.py`.
- For more complex automations, adjust the system prompt or max turn count to shape the agent's autonomy.
