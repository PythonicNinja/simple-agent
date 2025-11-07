"""Command line entry point for the simple agent."""

from __future__ import annotations

import argparse
from dataclasses import replace

from simple_agent import SimpleAgent, get_backend, load_default_tools
from simple_agent.config import get_settings


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run a small tool-enabled agent.")
    parser.add_argument("prompt", nargs="?", help="Prompt to send to the agent. If omitted, stdin is used.")
    parser.add_argument("--backend", choices=["chatgpt", "gemini"], help="Override the backend specified in .env.")
    parser.add_argument("--max-turns", type=int, default=5, help="Maximum number of tool loops before giving up.")
    parser.add_argument("--no-tools", action="store_true", help="Disable tool usage and respond directly.")
    parser.add_argument("--list-tools", action="store_true", help="List available tools and exit.")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    tools = [] if args.no_tools else load_default_tools()

    if args.list_tools:
        if not tools:
            print("No tools loaded.")
        else:
            for tool in tools:
                print(f"{tool.name}: {tool.description}")
        return

    prompt = args.prompt
    if not prompt:
        try:
            prompt = input("Prompt: ").strip()
        except EOFError:
            prompt = ""

    if not prompt:
        parser.error("A prompt is required.")

    settings = get_settings()
    if args.backend:
        settings = replace(settings, backend=args.backend)  # type: ignore[arg-type]

    backend = get_backend(settings)
    agent = SimpleAgent(backend=backend, tools=tools, system_prompt=settings.system_prompt)
    try:
        result = agent.run(prompt, max_turns=args.max_turns)
    except RuntimeError as exc:
        parser.exit(1, f"Error: {exc}\n")
    print(result)


if __name__ == "__main__":
    main()
