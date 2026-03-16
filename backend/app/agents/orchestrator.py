from typing import List, Dict, Any, Optional
import json
from datetime import datetime
import asyncio
from langchain.agents import initialize_agent, Tool, AgentType
from langchain.chat_models import ChatOpenAI
from langchain.llms import Ollama
from langchain.memory import ConversationBufferMemory
from langchain.callbacks import get_openai_callback
import logging

from app.config import settings

logger = logging.getLogger(__name__)


class AgentOrchestrator:
    """Orchestrates multi-agent workflows with LangChain"""
    
    def __init__(self):
        self.llm = None
        self.tool_registry: Dict[str, Tool] = {}
        self._init_llm()
    
    def _init_llm(self):
        """Initialize LLM based on configuration"""
        if settings.USE_OFFLINE_LLM and settings.OLLAMA_BASE_URL:
            self.llm = Ollama(
                base_url=settings.OLLAMA_BASE_URL,
                model=settings.OFFLINE_LLM_MODEL,
                temperature=settings.TEMPERATURE
            )
            logger.info(f"Using offline LLM: {settings.OFFLINE_LLM_MODEL}")
        else:
            if not settings.OPENAI_API_KEY:
                logger.warning("No OpenAI API key provided. Offline mode will be used.")
                self.llm = Ollama(
                    base_url=settings.OLLAMA_BASE_URL,
                    model=settings.OFFLINE_LLM_MODEL,
                    temperature=settings.TEMPERATURE
                )
            else:
                self.llm = ChatOpenAI(
                    model_name=settings.LLM_MODEL,
                    temperature=settings.TEMPERATURE,
                    max_tokens=settings.MAX_TOKENS,
                    api_key=settings.OPENAI_API_KEY
                )
                logger.info(f"Using OpenAI: {settings.LLM_MODEL}")
    
    def register_tool(self, tool: Tool):
        """Register a tool for agents to use"""
        self.tool_registry[tool.name] = tool
    
    def register_tools_batch(self, tools: List[Tool]):
        """Register multiple tools"""
        for tool in tools:
            self.register_tool(tool)
    
    def get_tools(self, tool_names: Optional[List[str]] = None) -> List[Tool]:
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
        
        # Create memory for the agent
        memory = ConversationBufferMemory(memory_key="chat_history")
        
        try:
            # Initialize agent
            agent = initialize_agent(
                tools=tools,
                llm=self.llm,
                agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
                memory=memory,
                verbose=settings.DEBUG,
                max_iterations=max_iterations,
            )
            
            # Prepare input
            input_prompt = self._prepare_prompt(task_objective, input_data)
            
            # Execute with token tracking
            with get_openai_callback() as cb:
                result = agent.run(input=input_prompt)
                tokens_used = cb.total_tokens
            
            return {
                "status": "completed",
                "result": result,
                "tokens_used": tokens_used,
                "reasoning_steps": self._extract_reasoning_steps(agent),
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
        # This would extract thought process from agent callbacks
        # Implementation depends on LangChain version and callbacks used
        return []
    
    def get_available_tools_info(self) -> List[Dict[str, Any]]:
        """Get information about available tools"""
        return [
            {
                "name": tool.name,
                "description": tool.description,
            }
            for tool in self.get_tools()
        ]


# Singleton instance
_orchestrator: Optional[AgentOrchestrator] = None


def get_orchestrator() -> AgentOrchestrator:
    """Get or create agent orchestrator instance"""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = AgentOrchestrator()
    return _orchestrator
