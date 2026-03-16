from typing import List, Dict, Any, Optional
import json
from datetime import datetime
import asyncio
import logging

from app.config import settings

logger = logging.getLogger(__name__)


class AgentOrchestrator:
    """Orchestrates multi-agent workflows"""
    
    def __init__(self):
        self.llm = None
        self.tool_registry: Dict[str, Any] = {}
        self._init_llm()
    
    def _init_llm(self):
        """Initialize LLM based on configuration"""
        # For now, using a simple mock implementation
        # In production, integrate with OpenAI or Ollama APIs directly
        logger.info(f"Agent orchestrator initialized in {settings.ENVIRONMENT} mode")
        self.llm = {"type": "mock", "model": "mock-model"}
    
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
        tool_names: Optional[List[str]] = None,
        input_data: Optional[Dict[str, Any]] = None,
        max_iterations: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Execute a single agent task with reasoning and planning"""
        
        max_iterations = max_iterations or settings.MAX_AGENT_ITERATIONS
        tools = self.get_tools(tool_names)
        
        try:
            # Simulate agent execution
            result = f"Agent '{agent_name}' processed objective: {task_objective}"
            if input_data:
                result += f" with input: {json.dumps(input_data)}"
            
            return {
                "status": "completed",
                "result": result,
                "tokens_used": 0,
                "reasoning_steps": [],
            }
        
        except Exception as e:
            logger.error(f"Agent execution failed: {str(e)}")
            return {
                "status": "failed",
                "error": str(e),
                "tokens_used": 0,
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
