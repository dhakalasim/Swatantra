from langchain.tools import Tool
from typing import Optional, Dict, Any
import json
import requests
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


def web_search(query: str) -> str:
    """
    Search the web for information.
    Useful for finding current information, news, or data online.
    """
    try:
        # This would integrate with a search API like SerpAPI or Google Custom Search
        # For demo purposes, returning a placeholder
        return f"Search results for: {query} (integration with search API needed)"
    except Exception as e:
        return f"Search failed: {str(e)}"


def execute_code(language: str, code: str) -> str:
    """
    Execute code snippets to perform calculations or data processing.
    Supported languages: python, javascript, bash
    """
    try:
        if language.lower() == "python":
            # Execute Python code safely (in production, use sandboxed execution)
            namespace = {}
            exec(code, namespace)
            return str(namespace.get("result", "Code executed successfully"))
        else:
            return f"Code execution for {language} not yet supported"
    except Exception as e:
        return f"Execution error: {str(e)}"


def read_file(file_path: str) -> str:
    """
    Read content from a file.
    Useful for document processing and data analysis.
    """
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        return content[:5000]  # Limit to 5000 chars
    except Exception as e:
        return f"Read error: {str(e)}"


def write_file(file_path: str, content: str) -> str:
    """
    Write content to a file.
    Useful for saving results and reports.
    """
    try:
        with open(file_path, 'w') as f:
            f.write(content)
        return f"Successfully wrote to {file_path}"
    except Exception as e:
        return f"Write error: {str(e)}"


def get_current_datetime() -> str:
    """
    Get the current date and time.
    Useful for timestamping events and scheduling.
    """
    return datetime.now().isoformat()


def make_http_request(
    method: str,
    url: str,
    headers: Optional[Dict[str, str]] = None,
    body: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Make HTTP requests to external APIs.
    Methods: GET, POST, PUT, DELETE
    """
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
        return response.text[:2000]  # Limit response
    except Exception as e:
        return f"HTTP request failed: {str(e)}"


def analyze_data(data_type: str, data: str) -> str:
    """
    Analyze data and extract insights.
    Supported types: json, csv, text
    """
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
    """
    Process documents: summarize, extract entities, or generate insights.
    Actions: summarize, extract_entities, generate_insights
    """
    try:
        if action == "summarize":
            # Simple summarization by taking first 3 sentences
            sentences = document_text.split('.')[:3]
            return '. '.join(sentences) + '.'
        elif action == "extract_entities":
            # Placeholder for entity extraction
            return "Entity extraction requires NER model"
        else:
            return f"Action '{action}' not recognized"
    except Exception as e:
        return f"Document processing error: {str(e)}"


# Register all tools
def get_default_tools() -> list:
    """Get list of default tools for agents"""
    tools = [
        Tool(
            name="web_search",
            func=web_search,
            description="Search the web for information. Input: search query"
        ),
        Tool(
            name="execute_code",
            func=lambda x: execute_code("python", x),
            description="Execute Python code. Input: Python code snippet"
        ),
        Tool(
            name="read_file",
            func=read_file,
            description="Read content from a file. Input: file path"
        ),
        Tool(
            name="write_file",
            func=lambda x: write_file(x.split('\n')[0], '\n'.join(x.split('\n')[1:])),
            description="Write content to a file. Input: 'file_path\\ncontent'"
        ),
        Tool(
            name="get_time",
            func=lambda x: get_current_datetime(),
            description="Get current date and time"
        ),
        Tool(
            name="http_request",
            func=lambda x: make_http_request("GET", x),
            description="Make HTTP GET request. Input: URL"
        ),
        Tool(
            name="analyze_data",
            func=lambda x: analyze_data("json", x),
            description="Analyze data (JSON, CSV, or text). Input: data"
        ),
        Tool(
            name="document_processor",
            func=lambda x: document_processor(x, "summarize"),
            description="Process documents (summarize, analyze). Input: document text"
        ),
    ]
    return tools


def get_tool_by_name(name: str) -> Optional[Tool]:
    """Get a tool by name"""
    tools_dict = {tool.name: tool for tool in get_default_tools()}
    return tools_dict.get(name)
