# backend/callback_handler.py
from langchain.callbacks.base import BaseCallbackHandler
from typing import Dict, List, Any

class ThinkingCallbackHandler(BaseCallbackHandler):
    """Callback handler for streaming agent thinking process."""
    
    def __init__(self, websocket=None):
        super().__init__()
        self.websocket = websocket
        self.thinking_steps = []
        
    async def on_llm_start(self, serialized: Dict[str, Any], prompts: List[str], **kwargs: Any) -> None:
        """Run when LLM starts running."""
        if self.websocket:
            await self.websocket.send_json({"type": "thinking", "content": "思考中..."})
    
    async def on_llm_new_token(self, token: str, **kwargs: Any) -> None:
        """Run on new LLM token."""
        if self.websocket:
            await self.websocket.send_json({"type": "token", "content": token})
    
    async def on_llm_end(self, response, **kwargs: Any) -> None:
        """Run when LLM ends running."""
        if self.websocket:
            await self.websocket.send_json({"type": "thinking_complete", "content": "思考完成"})
    
    async def on_tool_start(self, serialized: Dict[str, Any], input_str: str, **kwargs: Any) -> None:
        """Run when tool starts running."""
        tool_name = serialized.get("name", "未知工具")
        message = f"使用工具: {tool_name}\n输入: {input_str}"
        self.thinking_steps.append(message)
        if self.websocket:
            await self.websocket.send_json({"type": "tool_start", "content": message})
    
    async def on_tool_end(self, output: str, **kwargs: Any) -> None:
        """Run when tool ends running."""
        message = f"工具输出: {output}"
        self.thinking_steps.append(message)
        if self.websocket:
            await self.websocket.send_json({"type": "tool_end", "content": message})
    
    async def on_agent_action(self, action, **kwargs: Any) -> None:
        """Run on agent action."""
        message = f"执行动作: {action.tool}\n输入: {action.tool_input}"
        self.thinking_steps.append(message)
        if self.websocket:
            await self.websocket.send_json({"type": "agent_action", "content": message})
    
    async def on_agent_finish(self, finish, **kwargs: Any) -> None:
        """Run on agent end."""
        message = f"完成: {finish.return_values.get('output', '')}"
        self.thinking_steps.append(message)
        if self.websocket:
            await self.websocket.send_json({"type": "agent_finish", "content": message})