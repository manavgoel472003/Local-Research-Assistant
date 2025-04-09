# Local Research Assistant

A powerful research assistant that combines local LLM capabilities with web search to provide comprehensive research summaries on any topic.

## Features

- 🔍 Web search integration using Tavily API
- 🤖 Local LLM processing using Ollama
- 📝 Automatic research summarization
- 🔄 Iterative research refinement
- 🌐 Web interface for easy interaction
- 📊 Structured research output

## Prerequisites

- Python 3.8 or higher
- Ollama installed and running locally
- Tavily API key
- Flask (for web interface)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/manavgoel472003/Local-Research-Assistant.git
cd Local-Research-Assistant
```

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

3. Set up your environment:
   - Ensure Ollama is running locally
   - Set your Tavily API key in the code (currently in `local_research_agent.py`)

## Usage

### Web Interface

1. Start the Flask server:
```bash
python app.py
```

2. Open your web browser and navigate to `http://localhost:5000`

3. Enter your research topic in the search box and submit

### API Usage

The application also provides an API endpoint for programmatic access:

```python
import requests

response = requests.post('http://localhost:5000/api/search', 
                       json={'query': 'Your research topic here'})
result = response.json()
```

## Project Structure

- `app.py` - Flask web application
- `local_research_agent.py` - Core research agent implementation
- `templates/` - HTML templates for the web interface
- `requirements.txt` - Python dependencies

## How It Works

1. The agent takes a research topic as input
2. Generates targeted web search queries
3. Performs web searches using Tavily API (requires API key)
4. Processes and summarizes the results using local LLM
5. Iteratively refines the research through multiple passes
6. Returns a comprehensive summary

## Configuration

- The local LLM model can be configured in `local_research_agent.py`
- Web search parameters can be adjusted in the same file
- The number of research iterations can be modified in the code

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Acknowledgments

- [Ollama](https://ollama.ai/) for local LLM capabilities
- [Tavily](https://tavily.com/) for web search API
- [LangChain](https://www.langchain.com/) for LLM orchestration 
