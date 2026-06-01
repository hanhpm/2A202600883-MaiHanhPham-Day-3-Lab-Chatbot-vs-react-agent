import json
import re
from typing import Any, Callable, Dict, List, Optional, Tuple
from src.core.llm_provider import LLMProvider
from src.telemetry.logger import logger


class ReActAgent:
    """
    ReAct (Reasoning + Acting) Agent that follows the Thought-Action-Observation loop.
    """

    def __init__(self, llm: LLMProvider, tools: Dict[str, Callable], max_steps: int = 5):
        self.llm = llm
        self.tools = tools
        self.max_steps = max_steps
        self.history = []

    def get_system_prompt(self) -> str:
        """
        System prompt that instructs the agent to follow ReAct format.
        """
        tool_names = ", ".join(self.tools.keys())
        tool_descriptions = "\n".join(
            [f"- {name}: {self._get_tool_description(name)}" for name in self.tools.keys()]
        )

        return f"""You are a helpful lunch ordering assistant. You are an intelligent agent that reasons through problems step by step.

You have access to the following tools:
{tool_descriptions}

Use the following format exactly:
Thought: your reasoning about what to do next
Action: {{"tool": "tool_name", "args": {{...}}}}
Observation: [result from tool call]
... (repeat Thought/Action/Observation as needed)
Final Answer: your final response to the user

Rules:
1. Action MUST be valid JSON with "tool" and "args" keys
2. Only use tools from: {tool_names}
3. If you have enough information, provide Final Answer
4. Never invent data - only use tool results
5. Be concise and helpful

Let's begin:"""

    def _get_tool_description(self, tool_name: str) -> str:
        """Get description for a tool."""
        descriptions = {
            "search_menu": "Search menu items by price, spicy level, or category",
            "add_order": "Add a lunch order for a user",
            "update_order": "Update an existing order",
            "get_order": "Get order details for a user",
            "list_orders": "List all current orders",
            "mark_paid": "Mark an order as paid",
            "clear_orders": "Clear all orders",
            "summarize_orders": "Summarize all orders with total cost",
            "split_bill": "Calculate cost per user",
            "get_payment_status": "Check payment status",
            "check_missing_orders": "Check who hasn't ordered yet",
            "check_unpaid": "Check who hasn't paid yet",
            "get_members": "Get list of team members",
            "add_member": "Add a new team member",
            "remove_member": "Remove a team member",
        }
        return descriptions.get(tool_name, "Unknown tool")

    def run(self, user_input: str) -> Tuple[str, Dict[str, Any]]:
        """
        Run the ReAct agent loop.
        Returns: (final_answer, metrics)
        """
        logger.log_event("AGENT_START", {"input": user_input, "model": self.llm.model_name})

        system_prompt = self.get_system_prompt()
        scratchpad = ""
        steps = 0
        errors = []
        trace = []
        total_tokens = 0

        for step in range(self.max_steps):
            steps += 1

            # Build prompt with system, scratchpad, and user input
            prompt = f"{system_prompt}\n\n{scratchpad}\nUser: {user_input}\n"

            # Get LLM response
            llm_response, usage = self.llm.generate(prompt, system_prompt="")
            total_tokens += usage.get("total_tokens", 0)

            logger.log_event(
                "AGENT_STEP",
                {
                    "step": step,
                    "llm_response": llm_response[:200],  # First 200 chars for logging
                    "tokens": usage.get("total_tokens", 0),
                },
            )

            thought = self._extract_thought(llm_response)

            # Check for Final Answer
            if "Final Answer:" in llm_response:
                final_answer = llm_response.split("Final Answer:")[-1].strip()
                trace.append({
                    "step": step,
                    "thought": thought,
                    "final_answer": final_answer,
                })
                logger.log_event(
                    "AGENT_END",
                    {"steps": steps, "status": "success", "answer": final_answer[:100]},
                )
                return final_answer, {
                    "steps": steps,
                    "status": "success",
                    "total_tokens": total_tokens,
                    "errors": errors,
                    "trace": trace,
                }

            # Parse and execute action
            action = None
            try:
                action = self._parse_action(llm_response)
                observation = self._execute_tool(action)
            except Exception as e:
                error_msg = f"Error at step {step}: {str(e)}"
                errors.append(error_msg)
                logger.log_event("AGENT_ERROR", {"step": step, "error": error_msg})

                observation = json.dumps(
                    {"error": "ACTION_ERROR", "message": str(e)}, ensure_ascii=False
                )

            trace.append({
                "step": step,
                "thought": thought,
                "action": action,
                "observation": observation,
            })

            # Update scratchpad
            scratchpad += f"{llm_response}\nObservation: {observation}\n"

        # Max steps exceeded
        error_msg = "Max steps exceeded"
        logger.log_event("AGENT_END", {"steps": steps, "status": "failed", "reason": error_msg})

        return "Max steps reached. Please rephrase your request.", {
            "steps": steps,
            "status": "failed",
            "reason": error_msg,
            "errors": errors,
            "trace": trace,
            "total_tokens": total_tokens,
        }

    def _extract_thought(self, llm_response: str) -> str:
        """Extract Thought text from LLM response."""
        if "Thought:" not in llm_response:
            return ""
        after = llm_response.split("Thought:", 1)[1]
        for sep in ("\nAction:", "\nFinal Answer:", "\nObservation:"):
            if sep in after:
                after = after.split(sep, 1)[0]
                break
        return after.strip()

    def _parse_action(self, llm_response: str) -> Dict[str, Any]:
        """
        Parse Action JSON from LLM response.
        Format: Action: {"tool": "...", "args": {...}}
        """
        if "Action:" not in llm_response:
            raise ValueError("No Action found in response")

        action_text = llm_response.split("Action:")[-1].strip()

        # Extract JSON (first line usually)
        lines = action_text.split("\n")
        json_str = lines[0].strip()

        try:
            action = json.loads(json_str)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in Action: {json_str}") from e

        if "tool" not in action or "args" not in action:
            raise ValueError("Action must have 'tool' and 'args' keys")

        return action

    def _execute_tool(self, action: Dict[str, Any]) -> str:
        """
        Execute a tool and return result as JSON string.
        """
        tool_name = action.get("tool")
        args = action.get("args", {})

        if tool_name not in self.tools:
            return json.dumps(
                {"error": "UNKNOWN_TOOL", "message": f"Tool '{tool_name}' not found"},
                ensure_ascii=False,
            )

        try:
            tool_func = self.tools[tool_name]
            result = tool_func(**args)

            # Ensure result is JSON-serializable
            if isinstance(result, (dict, list, str, int, float, bool, type(None))):
                return json.dumps(result, ensure_ascii=False)
            else:
                return json.dumps({"result": str(result)}, ensure_ascii=False)

        except TypeError as e:
            return json.dumps(
                {"error": "INVALID_ARGUMENTS", "message": f"Invalid arguments: {str(e)}"},
                ensure_ascii=False,
            )
        except Exception as e:
            return json.dumps(
                {"error": "TOOL_ERROR", "message": f"Tool error: {str(e)}"}, ensure_ascii=False
            )
