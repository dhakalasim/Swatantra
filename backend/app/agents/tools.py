from typing import Optional, Dict, Any, Callable
import json
import re
import html as html_module
import requests
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


def _duckduckgo_instant_answer(query: str) -> Optional[str]:
    """Fast path: DuckDuckGo's Instant Answer API. Only has canned answers for
    a narrow set of canonical topics (e.g. named entities like 'Mount
    Everest') — returns None for anything it doesn't recognize, which is most
    real questions."""
    response = requests.get(
        "https://api.duckduckgo.com/",
        params={"q": query, "format": "json", "no_html": 1, "skip_disambig": 1},
        timeout=8,
    )
    response.raise_for_status()
    data = response.json()

    if data.get("AbstractText"):
        source = data.get("AbstractSource") or "DuckDuckGo"
        return f"{data['AbstractText']} (Source: {source})"

    related = [
        topic["Text"]
        for topic in data.get("RelatedTopics", [])
        if isinstance(topic, dict) and topic.get("Text")
    ]
    if related:
        return "\n".join(related[:3])

    return None


_WIKI_TAG_RE = re.compile(r"<[^>]+>")


def _wikipedia_search(query: str, max_results: int = 3) -> Optional[str]:
    """Broad fallback covering arbitrary real-world questions. Wikipedia's
    search API is free, keyless, and (unlike scraping a search engine's HTML
    results page) isn't bot-blocked, so it's a reliable way to actually
    answer whatever the user searches for."""
    response = requests.get(
        "https://en.wikipedia.org/w/api.php",
        params={
            "action": "query",
            "list": "search",
            "srsearch": query,
            "format": "json",
            "srlimit": max_results,
        },
        headers={"User-Agent": "SwatantraAgent/1.0"},
        timeout=8,
    )
    response.raise_for_status()
    results = response.json().get("query", {}).get("search", [])
    if not results:
        return None

    lines = []
    for item in results:
        title = item.get("title", "Untitled")
        snippet = html_module.unescape(_WIKI_TAG_RE.sub("", item.get("snippet", ""))).strip()
        lines.append(f"- {title}: {snippet} (Source: Wikipedia)")
    return "\n".join(lines)


# Tool definitions as dictionaries for compatibility
def web_search(query: str) -> str:
    """Search the web for information. Tries DuckDuckGo's Instant Answer API
    first for canonical topics, then falls back to Wikipedia's search API so
    arbitrary questions still get a real, useful answer instead of 'no
    result found'."""
    try:
        answer = _duckduckgo_instant_answer(query)
        if answer:
            return answer
    except requests.RequestException as e:
        logger.warning(f"DuckDuckGo instant-answer lookup failed for {query!r}: {e}")

    try:
        answer = _wikipedia_search(query)
        if answer:
            return answer
    except requests.RequestException as e:
        logger.warning(f"Wikipedia search fallback failed for {query!r}: {e}")
        return f"Web search failed: {e}"

    return f"No results found for '{query}'. Try rephrasing your query."


def execute_code(language: str, code: str) -> str:
    """Execute code snippets."""
    if language.lower() == "python":
        try:
            namespace = {}
            exec(code, namespace)
            return str(namespace.get("result", "Code executed successfully"))
        except Exception as e:
            return f"Execution error: {str(e)}"
    return f"Code execution for {language} not yet supported"


def read_file(file_path: str) -> str:
    """Read content from a file."""
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        return content[:5000]
    except Exception as e:
        return f"Read error: {str(e)}"


def write_file(file_path: str, content: str) -> str:
    """Write content to a file."""
    try:
        with open(file_path, 'w') as f:
            f.write(content)
        return f"Successfully wrote to {file_path}"
    except Exception as e:
        return f"Write error: {str(e)}"


def get_current_datetime() -> str:
    """Get the current date and time."""
    return datetime.now().isoformat()


def make_http_request(method: str, url: str, headers: Optional[Dict] = None, body: Optional[Dict] = None) -> str:
    """Make HTTP requests to external APIs."""
    try:
        if method.upper() == "GET":
            response = requests.get(url, headers=headers)
        elif method.upper() == "POST":
            response = requests.post(url, json=body, headers=headers)
        elif method.upper() == "PUT":
            response = requests.put(url, json=body, headers=headers)
        elif method.upper() == "DELETE":
            response = requests.delete(url, headers=headers)
        else:
            return f"Unsupported HTTP method: {method}"
        
        response.raise_for_status()
        return response.text[:2000]
    except Exception as e:
        return f"HTTP request failed: {str(e)}"


def analyze_data(data_type: str, data: str) -> str:
    """Analyze data and extract insights."""
    try:
        if data_type.lower() == "json":
            parsed = json.loads(data)
            return f"JSON analysis: {len(parsed)} top-level keys"
        elif data_type.lower() == "csv":
            lines = data.split('\n')
            return f"CSV analysis: {len(lines)} rows"
        else:
            words = len(data.split())
            return f"Text analysis: {words} words"
    except Exception as e:
        return f"Analysis error: {str(e)}"


def document_processor(document_text: str, action: str = "summarize") -> str:
    """Process documents."""
    try:
        if action == "summarize":
            sentences = document_text.split('.')[:3]
            return '. '.join(sentences) + '.'
        elif action == "extract_entities":
            return "Entity extraction requires NER model"
        else:
            return f"Action '{action}' not recognized"
    except Exception as e:
        return f"Document processing error: {str(e)}"


# Tool registry as dictionaries
TOOLS = [
    {
        "name": "web_search",
        "func": web_search,
        "description": "Search the web for information. Input: search query"
    },
    {
        "name": "execute_code",
        "func": execute_code,
        "description": "Execute Python code. Input: Python code snippet"
    },
    {
        "name": "read_file",
        "func": read_file,
        "description": "Read content from a file. Input: file path"
    },
    {
        "name": "write_file",
        "func": write_file,
        "description": "Write content to a file. Input: 'file_path\\ncontent'"
    },
    {
        "name": "get_time",
        "func": get_current_datetime,
        "description": "Get current date and time"
    },
    {
        "name": "http_request",
        "func": make_http_request,
        "description": "Make HTTP GET request. Input: URL"
    },
    {
        "name": "analyze_data",
        "func": analyze_data,
        "description": "Analyze data (JSON, CSV, or text). Input: data"
    },
    {
        "name": "document_processor",
        "func": document_processor,
        "description": "Process documents (summarize, analyze). Input: document text"
    },
]


def get_default_tools() -> list:
    """Get list of default tools for agents"""
    return TOOLS


def get_tool_by_name(name: str) -> Optional[Dict]:
    """Get a tool by name"""
    for tool in TOOLS:
        if tool["name"] == name:
            return tool
    return None


# JSON Schema tool definitions for the Claude tool-use loop (see
# app/agents/orchestrator.py). Each schema's parameter names match the
# corresponding function's keyword arguments exactly, so a tool_use block's
# `input` dict can be passed straight through as **kwargs.
CLAUDE_TOOL_SCHEMAS = [
    {
        "name": "web_search",
        "description": (
            "Search the web for current information, facts, or anything not "
            "already known. Use this whenever the answer depends on "
            "up-to-date or specific real-world information."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "The search query"},
            },
            "required": ["query"],
        },
    },
    {
        "name": "execute_code",
        "description": "Execute a short Python code snippet and return its result. Assign the final answer to a variable named `result`.",
        "input_schema": {
            "type": "object",
            "properties": {
                "language": {"type": "string", "description": "Programming language, e.g. 'python' (currently the only supported value)"},
                "code": {"type": "string", "description": "The code to execute"},
            },
            "required": ["language", "code"],
        },
    },
    {
        "name": "read_file",
        "description": "Read the contents of a file from the local filesystem.",
        "input_schema": {
            "type": "object",
            "properties": {
                "file_path": {"type": "string", "description": "Path to the file to read"},
            },
            "required": ["file_path"],
        },
    },
    {
        "name": "write_file",
        "description": "Write content to a file on the local filesystem, creating or overwriting it.",
        "input_schema": {
            "type": "object",
            "properties": {
                "file_path": {"type": "string", "description": "Path to the file to write"},
                "content": {"type": "string", "description": "Content to write to the file"},
            },
            "required": ["file_path", "content"],
        },
    },
    {
        "name": "get_time",
        "description": "Get the current date and time.",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "http_request",
        "description": "Make an HTTP request (GET, POST, PUT, or DELETE) to an external API or URL.",
        "input_schema": {
            "type": "object",
            "properties": {
                "method": {"type": "string", "enum": ["GET", "POST", "PUT", "DELETE"]},
                "url": {"type": "string", "description": "The URL to request"},
                "headers": {"type": "object", "description": "Optional HTTP headers"},
                "body": {"type": "object", "description": "Optional JSON request body"},
            },
            "required": ["method", "url"],
        },
    },
    {
        "name": "analyze_data",
        "description": "Analyze a blob of data (JSON, CSV, or plain text) and report basic structural insights.",
        "input_schema": {
            "type": "object",
            "properties": {
                "data_type": {"type": "string", "enum": ["json", "csv", "text"]},
                "data": {"type": "string", "description": "The raw data to analyze"},
            },
            "required": ["data_type", "data"],
        },
    },
    {
        "name": "document_processor",
        "description": "Summarize or otherwise process a block of document text.",
        "input_schema": {
            "type": "object",
            "properties": {
                "document_text": {"type": "string", "description": "The document text to process"},
                "action": {"type": "string", "enum": ["summarize", "extract_entities"], "description": "Defaults to 'summarize'"},
            },
            "required": ["document_text"],
        },
    },
]


def get_claude_tool_schemas(allowed_names: Optional[list] = None) -> list:
    """Return Claude tool-use schemas, optionally filtered to an allowed subset."""
    if allowed_names is None:
        return CLAUDE_TOOL_SCHEMAS
    return [t for t in CLAUDE_TOOL_SCHEMAS if t["name"] in allowed_names]
