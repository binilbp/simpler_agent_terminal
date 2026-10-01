# Simple Agent Terminal

A simple terminal-based AI agent built with Python, LangGraph, and Textual.

The project provides a terminal user interface for interacting with an OS using LLM-powered agent.It is mainly intended to operate Linux using natural commands

It uses:

* **Python** for the application
* **Textual** for the terminal UI
* **LangGraph** for agent orchestration
* **Ollama** for local LLMs
* **Groq** for hosted LLMs

## Installation

Clone the repository:

```bash
git clone https://github.com/binilbp/simpler_agent_terminal.git
cd simpler_agent_terminal
```

Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

## Configuration

Create a `.env` file in the project root and add the required API keys for the provider you want to use.

For Groq:

```env
GROQ_API_KEY=your_api_key
```

For Ollama, make sure Ollama is installed and running locally.

## Running

Start the agent with:

```bash
python main.py
```

The terminal UI will start and you can interact with the agent from there.

## License

This project is licensed under the GNU General Public License v3.0.
