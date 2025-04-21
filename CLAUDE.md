# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands
- Run the app: `python main.py`
- Install dependencies: `pip install -r requirements.txt`
- Format code: `black .` (recommended, not enforced)
- Type checking: `mypy .` (recommended, not enforced)

## Code Style Guidelines
- Use 4-space indentation
- Follow PEP 8 naming conventions (snake_case for variables/functions)
- Import order: standard library → third-party → local
- Document functions with docstrings
- Use f-strings for string formatting
- Place blank lines between functions and logical sections
- Error handling: Catch specific exceptions with helpful error messages
- Type hints are encouraged but not strictly required

## Project Structure
Terminal-based multi-client chat application supporting OpenAI, Anthropic, and Mistral AI models simultaneously.