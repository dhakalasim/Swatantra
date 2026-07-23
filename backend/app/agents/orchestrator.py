from typing import List, Dict, Any, Optional, Tuple
import json
import time
from datetime import datetime
import asyncio
import logging

from app.config import settings
from app.agents.tools import get_tool_by_name, get_claude_tool_schemas

logger = logging.getLogger(__name__)

try:
    import anthropic
except ImportError:  # pragma: no cover - optional dependency until installed
    anthropic = None


# Keyword -> tool routing. Checked in order; first match wins. This is a
# lightweight rule-based planner (no LLM is configured), not real reasoning.
TOOL_KEYWORDS: List[Tuple[str, List[str]]] = [
    ("read_file", ["read file", "read the file", "load file", "open file"]),
    ("write_file", ["write file", "write to file", "save file", "create file"]),
    ("execute_code", ["run code", "execute code", "run python", "execute python"]),
    ("http_request", ["http request", "call api", "call the api", "fetch url", "make a request"]),
    ("get_time", ["current time", "current date", "what time", "what date", "today's date"]),
    ("analyze_data", ["analyze data", "analyse data", "data analysis"]),
    ("document_processor", ["summarize", "summarise", "document"]),
    ("web_search", ["search", "look up", "find information", "google"]),
]


def _build_tool_params(tool_name: str, input_data: Dict[str, Any], objective: str) -> Optional[Dict[str, Any]]:
    """Derive concrete function arguments for a tool from task input_data.
    Returns None if required parameters are missing."""
    d = input_data or {}

    if tool_name == "read_file":
        file_path = d.get("file_path")
        return {"file_path": file_path} if file_path else None

    if tool_name == "write_file":
        file_path, content = d.get("file_path"), d.get("content")
        return {"file_path": file_path, "content": content} if file_path and content is not None else None

    if tool_name == "execute_code":
        code = d.get("code")
        return {"language": d.get("language", "python"), "code": code} if code else None

    if tool_name == "http_request":
        url = d.get("url")
        if not url:
            return None
        return {"method": d.get("method", "GET"), "url": url, "headers": d.get("headers"), "body": d.get("body")}

    if tool_name == "get_time":
        return {}

    if tool_name == "analyze_data":
        data = d.get("data")
        return {"data_type": d.get("data_type", "text"), "data": data} if data else None

    if tool_name == "document_processor":
        text = d.get("document_text") or d.get("text")
        return {"document_text": text, "action": d.get("action", "summarize")} if text else None

    if tool_name == "web_search":
        return {"query": d.get("query") or objective}

    return None


class AgentOrchestrator:
    """Orchestrates agent task execution.

    When ANTHROPIC_API_KEY is configured, tasks run through a real ReAct-style
    tool-use loop against Claude: the model reasons about the objective,
    decides which tool(s) to call (if any), sees each tool's result, and
    keeps iterating — genuinely chaining multiple tools per task — until it
    produces a final answer or MAX_AGENT_ITERATIONS is reached.

    Without a key (offline / no credentials), execution falls back to a
    simple, honest rule-based router: it matches the task objective against
    known tool keywords (or an explicit input_data['tool'] override) and
    invokes exactly one tool. This keeps the app fully functional offline,
    it just isn't "real" reasoning.
    """

    def __init__(self):
        self.llm = None
        self.client: Optional["anthropic.Anthropic"] = None
        self.use_claude = False
        self.tool_registry: Dict[str, Any] = {}
        self._init_llm()

    def _init_llm(self):
        """Initialize the reasoning engine based on configuration."""
        if settings.ANTHROPIC_API_KEY and anthropic is not None:
            self.client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
            self.use_claude = True
            self.llm = {"type": "anthropic", "model": settings.ANTHROPIC_MODEL}
            logger.info(f"Agent orchestrator using Claude ({settings.ANTHROPIC_MODEL}) for real agentic reasoning")
        else:
            if settings.ANTHROPIC_API_KEY and anthropic is None:
                logger.warning("ANTHROPIC_API_KEY is set but the 'anthropic' package is not installed — falling back to rule-based routing")
            self.use_claude = False
            self.llm = {"type": "mock", "model": "mock-model"}
            logger.info(f"Agent orchestrator initialized in {settings.ENVIRONMENT} mode (no ANTHROPIC_API_KEY — rule-based fallback)")

    def _normalize_tool_names(self, tool_names: Optional[List[Any]]) -> Optional[List[str]]:
        """Accepts either a list of tool name strings or a list of
        {"name": ..., "enabled": ...} dicts (as stored on Agent.tools) and
        returns the list of enabled tool name strings, or None (= all tools allowed)."""
        if not tool_names:
            return None

        names = []
        for entry in tool_names:
            if isinstance(entry, str):
                names.append(entry)
            elif isinstance(entry, dict) and entry.get("enabled", True):
                name = entry.get("name")
                if name:
                    names.append(name)
        return names or None

    def _select_tool(
        self,
        objective: str,
        input_data: Dict[str, Any],
        allowed_tool_names: Optional[List[str]],
    ) -> Tuple[Optional[str], Optional[Dict[str, Any]]]:
        """Pick a tool and its parameters for the given objective."""
        objective_lower = (objective or "").lower()

        def is_allowed(name: str) -> bool:
            return allowed_tool_names is None or name in allowed_tool_names

        # Explicit override: input_data = {"tool": "web_search", "query": "..."}
        explicit = (input_data or {}).get("tool")
        if explicit and is_allowed(explicit):
            params = _build_tool_params(explicit, input_data, objective)
            if params is not None:
                return explicit, params

        # Keyword routing
        for tool_name, keywords in TOOL_KEYWORDS:
            if not is_allowed(tool_name):
                continue
            if any(keyword in objective_lower for keyword in keywords):
                params = _build_tool_params(tool_name, input_data, objective)
                if params is not None:
                    return tool_name, params

        # Default fallback: treat the objective as a web search query.
        if is_allowed("web_search"):
            return "web_search", {"query": objective}

        return None, None
    
    def register_tool(self, tool: Any):
        """Register a tool for agents to use"""
        if hasattr(tool, 'name'):
            self.tool_registry[tool.name] = tool
        elif isinstance(tool, dict):
            self.tool_registry[tool.get('name', 'unknown')] = tool
    
    def register_tools_batch(self, tools: List[Any]):
        """Register multiple tools"""
        for tool in tools:
            self.register_tool(tool)
    
    def get_tools(self, tool_names: Optional[List[str]] = None) -> List[Any]:
        """Get tools by name or all registered tools"""
        if tool_names:
            return [self.tool_registry[name] for name in tool_names if name in self.tool_registry]
        return list(self.tool_registry.values())
    
    async def execute_agent_task(
        self,
        task_objective: str,
        agent_name: str,
        tool_names: Optional[List[Any]] = None,
        input_data: Optional[Dict[str, Any]] = None,
        max_iterations: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Execute a single agent task.

        Routes to the real Claude ReAct loop when configured, otherwise to
        the rule-based single-tool fallback.
        """
        input_data = input_data or {}
        allowed_tool_names = self._normalize_tool_names(tool_names)

        if self.use_claude:
            return await self._execute_claude_agent(
                task_objective=task_objective,
                agent_name=agent_name,
                allowed_tool_names=allowed_tool_names,
                input_data=input_data,
                max_iterations=max_iterations or settings.MAX_AGENT_ITERATIONS,
            )

        return self._execute_rule_based(task_objective, agent_name, allowed_tool_names, input_data)

    async def _execute_claude_agent(
        self,
        task_objective: str,
        agent_name: str,
        allowed_tool_names: Optional[List[str]],
        input_data: Dict[str, Any],
        max_iterations: int,
    ) -> Dict[str, Any]:
        """Real multi-step ReAct loop: Claude decides which tool(s) to call,
        sees each result, and keeps reasoning until it has a final answer."""

        start = time.time()
        tool_schemas = get_claude_tool_schemas(allowed_tool_names)

        system_prompt = (
            f"You are '{agent_name}', an autonomous agent in the Swatantra platform. "
            "Break the user's objective down and use the available tools whenever they "
            "would help — you may call multiple tools, one after another, chaining their "
            "results together, before giving your final answer. If no tool is needed, "
            "answer directly. Be concise and give a clear final answer once you are done."
        )

        user_content = f"Objective: {task_objective}"
        if input_data:
            extra = {k: v for k, v in input_data.items() if k != "tool"}
            if extra:
                user_content += f"\n\nAdditional context:\n{json.dumps(extra, default=str)}"

        messages: List[Dict[str, Any]] = [{"role": "user", "content": user_content}]

        reasoning_steps: List[Dict[str, Any]] = []
        tools_used: List[str] = []
        total_tokens = 0
        step_number = 0

        try:
            for _ in range(max_iterations):
                response = self.client.messages.create(
                    model=settings.ANTHROPIC_MODEL,
                    max_tokens=4096,
                    system=system_prompt,
                    messages=messages,
                    tools=tool_schemas if tool_schemas else None,
                    output_config={"effort": settings.AGENT_EFFORT},
                )

                usage = getattr(response, "usage", None)
                if usage:
                    total_tokens += (usage.input_tokens or 0) + (usage.output_tokens or 0)

                assistant_content = []
                tool_use_blocks = []
                final_text_parts = []

                for block in response.content:
                    if block.type == "text":
                        assistant_content.append({"type": "text", "text": block.text})
                        final_text_parts.append(block.text)
                        if block.text.strip():
                            step_number += 1
                            reasoning_steps.append({
                                "step_number": step_number,
                                "action_type": "reasoning",
                                "description": block.text.strip(),
                            })
                    elif block.type == "tool_use":
                        assistant_content.append({
                            "type": "tool_use",
                            "id": block.id,
                            "name": block.name,
                            "input": block.input,
                        })
                        tool_use_blocks.append(block)

                messages.append({"role": "assistant", "content": assistant_content})

                if response.stop_reason != "tool_use" or not tool_use_blocks:
                    final_text = "\n".join(p for p in final_text_parts if p.strip()) or task_objective
                    return {
                        "status": "completed",
                        "result": final_text,
                        "tool_used": tools_used[-1] if tools_used else None,
                        "tools_used": tools_used,
                        "tokens_used": total_tokens,
                        "reasoning_steps": reasoning_steps,
                        "execution_time_seconds": round(time.time() - start, 3),
                        "engine": "claude",
                    }

                # Execute every requested tool and feed all results back in one turn.
                tool_results = []
                for tool_block in tool_use_blocks:
                    tool_name = tool_block.name
                    tool_input = tool_block.input or {}
                    tool = get_tool_by_name(tool_name)

                    step_number += 1
                    if not tool:
                        error_text = f"Unknown tool '{tool_name}'"
                        reasoning_steps.append({
                            "step_number": step_number,
                            "action_type": "tool_call",
                            "description": error_text,
                        })
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": tool_block.id,
                            "content": error_text,
                            "is_error": True,
                        })
                        continue

                    try:
                        output = tool["func"](**tool_input)
                        tools_used.append(tool_name)
                        reasoning_steps.append({
                            "step_number": step_number,
                            "action_type": "tool_call",
                            "description": f"Called '{tool_name}' with {tool_input}",
                            "output": {"value": str(output)[:2000]},
                        })
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": tool_block.id,
                            "content": str(output)[:8000],
                        })
                    except Exception as e:
                        logger.error(f"Tool '{tool_name}' raised an error: {e}")
                        reasoning_steps.append({
                            "step_number": step_number,
                            "action_type": "tool_call",
                            "description": f"Tool '{tool_name}' raised an error: {e}",
                        })
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": tool_block.id,
                            "content": f"Error: {e}",
                            "is_error": True,
                        })

                messages.append({"role": "user", "content": tool_results})

            # Ran out of iterations without a final answer.
            return {
                "status": "completed",
                "result": "Reached the maximum number of reasoning steps before finishing. Try narrowing the objective.",
                "tool_used": tools_used[-1] if tools_used else None,
                "tools_used": tools_used,
                "tokens_used": total_tokens,
                "reasoning_steps": reasoning_steps,
                "execution_time_seconds": round(time.time() - start, 3),
                "engine": "claude",
            }

        except Exception as e:
            logger.error(f"Claude agent execution failed: {e}")
            return {
                "status": "failed",
                "error": str(e),
                "tool_used": tools_used[-1] if tools_used else None,
                "tools_used": tools_used,
                "tokens_used": total_tokens,
                "reasoning_steps": reasoning_steps,
                "engine": "claude",
            }

    def _execute_rule_based(
        self,
        task_objective: str,
        agent_name: str,
        allowed_tool_names: Optional[List[str]],
        input_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Select a single tool via keyword routing (or an explicit
        input_data['tool'] override) and actually run it. Used when no
        ANTHROPIC_API_KEY is configured."""

        reasoning_steps = [
            {
                "step_number": 1,
                "action_type": "reasoning",
                "description": f"Analyzing objective for agent '{agent_name}': {task_objective!r}",
            }
        ]

        tool_name, params = self._select_tool(task_objective, input_data, allowed_tool_names)

        if not tool_name:
            reasoning_steps.append({
                "step_number": 2,
                "action_type": "reasoning",
                "description": "No enabled tool matched this objective.",
            })
            return {
                "status": "completed",
                "result": task_objective,
                "tool_used": None,
                "tools_used": [],
                "tokens_used": 0,
                "reasoning_steps": reasoning_steps,
                "engine": "rule_based",
            }

        reasoning_steps.append({
            "step_number": 2,
            "action_type": "decision",
            "description": f"Selected tool '{tool_name}' with parameters {params}",
        })

        tool = get_tool_by_name(tool_name)
        start = time.time()

        try:
            output = tool["func"](**params)
            reasoning_steps.append({
                "step_number": 3,
                "action_type": "tool_call",
                "description": f"Executed tool '{tool_name}'",
                "output": {"value": str(output)[:2000]},
            })

            return {
                "status": "completed",
                "result": output,
                "tool_used": tool_name,
                "tools_used": [tool_name],
                "tool_params": params,
                "tokens_used": 0,
                "reasoning_steps": reasoning_steps,
                "execution_time_seconds": round(time.time() - start, 3),
                "engine": "rule_based",
            }

        except Exception as e:
            logger.error(f"Agent execution failed while running tool '{tool_name}': {str(e)}")
            reasoning_steps.append({
                "step_number": 3,
                "action_type": "tool_call",
                "description": f"Tool '{tool_name}' raised an error: {str(e)}",
            })
            return {
                "status": "failed",
                "error": str(e),
                "tool_used": tool_name,
                "tools_used": [tool_name],
                "tokens_used": 0,
                "reasoning_steps": reasoning_steps,
                "engine": "rule_based",
            }
    
    async def execute_multi_agent_workflow(
        self,
        workflow_steps: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Execute a multi-agent workflow with step coordination"""
        
        execution_log = []
        current_context = context or {}
        
        for step_idx, step in enumerate(workflow_steps):
            step_name = step.get("name", f"Step_{step_idx}")
            agent_name = step.get("agent", "default")
            objective = step.get("objective")
            tool_names = step.get("tools", [])
            
            logger.info(f"Executing workflow step: {step_name}")
            
            # Execute step
            result = await self.execute_agent_task(
                task_objective=objective,
                agent_name=agent_name,
                tool_names=tool_names,
                input_data=current_context
            )
            
            execution_log.append({
                "step": step_idx,
                "name": step_name,
                "result": result,
                "timestamp": datetime.utcnow().isoformat(),
            })
            
            # Update context with step result
            if result["status"] == "completed":
                current_context.update(result.get("result", {}))
            else:
                logger.error(f"Step {step_name} failed: {result.get('error')}")
                break
        
        return {
            "status": "completed" if all(s["result"]["status"] == "completed" for s in execution_log) else "partial",
            "steps_executed": len(execution_log),
            "execution_log": execution_log,
            "final_context": current_context,
        }
    
    def _prepare_prompt(
        self,
        objective: str,
        input_data: Optional[Dict[str, Any]] = None
    ) -> str:
        """Prepare a structured prompt for the agent"""
        
        prompt = f"Objective: {objective}\n"
        
        if input_data:
            prompt += "\nInput Data:\n"
            for key, value in input_data.items():
                if isinstance(value, (dict, list)):
                    prompt += f"  {key}: {json.dumps(value)}\n"
                else:
                    prompt += f"  {key}: {value}\n"
        
        prompt += "\nPlease analyze this objective and execute the necessary steps using available tools."
        
        return prompt
    
    def _extract_reasoning_steps(self, agent) -> List[Dict[str, Any]]:
        """Extract reasoning steps from agent execution"""
        # Placeholder for reasoning extraction
        return []
    
    def get_available_tools_info(self) -> List[Dict[str, Any]]:
        """Get information about available tools"""
        tools_info = []
        for tool in self.get_tools():
            if isinstance(tool, dict):
                tools_info.append({
                    "name": tool.get("name", "unknown"),
                    "description": tool.get("description", "No description"),
                })
            else:
                tools_info.append({
                    "name": getattr(tool, 'name', 'unknown'),
                    "description": getattr(tool, 'description', 'No description'),
                })
        return tools_info


# Singleton instance
_orchestrator: Optional[AgentOrchestrator] = None


def get_orchestrator() -> AgentOrchestrator:
    """Get or create agent orchestrator instance"""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = AgentOrchestrator()
    return _orchestrator
