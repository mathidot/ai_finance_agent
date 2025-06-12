# backend/callback_handler.py
from langchain.callbacks.base import BaseCallbackHandler
from typing import Dict, List, Any
import json
import datetime
import traceback

class ThinkingCallbackHandler(BaseCallbackHandler):
    """Callback handler for streaming agent thinking process with enhanced formatting."""
    
    def __init__(self, websocket=None):
        super().__init__()
        self.websocket = websocket
        self.thinking_steps = []
        self.start_time = datetime.datetime.now()
        
    async def _send_message(self, message_type: str, content: str) -> None:
        """Helper method to send formatted messages to websocket."""
        try:
            if self.websocket:
                # 添加时间戳
                elapsed = (datetime.datetime.now() - self.start_time).total_seconds()
                timestamp = f"[{elapsed:.2f}s] "
                
                # 发送消息
                await self.websocket.send_json({
                    "type": message_type,
                    "content": timestamp + content,
                    "timestamp": elapsed
                })
        except Exception as e:
            print(f"Error sending websocket message: {e}")
            traceback.print_exc()
    
    async def on_llm_start(self, serialized: Dict[str, Any], prompts: List[str], **kwargs: Any) -> None:
        """Run when LLM starts running."""
        message = "🤔 开始思考您的问题..."
        self.thinking_steps.append(message)
        await self._send_message("thinking", message)
    
    async def on_llm_end(self, response, **kwargs: Any) -> None:
        """Run when LLM ends running."""
        message = "✅ 初步思考完成"
        self.thinking_steps.append(message)
        await self._send_message("thinking_complete", message)
    
    async def on_tool_start(self, serialized: Dict[str, Any], input_str: str, **kwargs: Any) -> None:
        """Run when tool starts running."""
        tool_name = serialized.get("name", "未知工具")
        
        # 为不同工具添加图标
        icon = "🔍" # 默认图标
        if "search" in tool_name.lower():
            icon = "🔍"
        elif "stock" in tool_name.lower():
            icon = "📈"
        elif "analyst" in tool_name.lower():
            icon = "👨‍💼"
        elif "fundamental" in tool_name.lower():
            icon = "📊"
            
        # 格式化消息
        message = f"{icon} **使用工具**: `{tool_name}`\n**输入**: ```\n{input_str}\n```"
        self.thinking_steps.append(message)
        await self._send_message("tool_start", message)
    
    async def on_tool_end(self, output: str, **kwargs: Any) -> None:
        """Run when tool ends running."""
        # 尝试格式化输出（如果是JSON）
        formatted_output = output
        try:
            # 检查输出是否是JSON字符串
            if output.strip().startswith('{') or output.strip().startswith('['):
                parsed = json.loads(output)
                formatted_output = json.dumps(parsed, indent=2, ensure_ascii=False)
        except:
            # 如果不是JSON或解析失败，使用原始输出
            pass
            
        # 如果输出太长，截断它
        if len(formatted_output) > 1000:
            formatted_output = formatted_output[:1000] + "\n... (输出已截断，共 " + str(len(output)) + " 字符)"
            
        message = f"📋 **工具输出**:\n```\n{formatted_output}\n```"
        self.thinking_steps.append(message)
        await self._send_message("tool_end", message)
    
    async def on_agent_action(self, action, **kwargs: Any) -> None:
        """Run on agent action."""
        # 为不同动作添加图标
        icon = "🔧" # 默认图标
        if "search" in action.tool.lower():
            icon = "🔍"
        elif "stock" in action.tool.lower():
            icon = "📈"
        elif "analyst" in action.tool.lower():
            icon = "👨‍💼"
        elif "fundamental" in action.tool.lower():
            icon = "📊"
            
        # 格式化消息
        message = f"{icon} **执行动作**: `{action.tool}`\n**输入参数**: ```\n{action.tool_input}\n```"
        self.thinking_steps.append(message)
        await self._send_message("agent_action", message)
    
    async def on_agent_finish(self, finish, **kwargs: Any) -> None:
        """Run on agent end."""
        output = finish.return_values.get('output', '')
        # 如果输出太长，截断它
        if len(output) > 500:
            short_output = output[:500] + "... (输出已截断)"
        else:
            short_output = output
            
        message = f"✅ **分析完成**\n\n{short_output}"
        self.thinking_steps.append(message)
        await self._send_message("agent_finish", message)