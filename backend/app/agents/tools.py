from typing import Optional, Dict, Any, Callable
import json
import requests
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


# Tool definitions as dictionaries for compatibility
def web_search(query: str) -> str:
    """Search the web for information."""
    return f"Search results for: {query} (Integration with search API needed)"


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
