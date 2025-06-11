// frontend/src/services/websocket.ts
import { WS_CHAT_ENDPOINT } from './config';

type MessageCallback = (message: string) => void;
type ThinkingCallback = (thinking: string) => void;
type ErrorCallback = (error: string) => void;
type ConnectionCallback = () => void;

interface WebSocketHandlers {
  onMessage: MessageCallback;
  onThinking: ThinkingCallback;
  onError: ErrorCallback;
  onOpen?: ConnectionCallback;
  onClose?: ConnectionCallback;
}

export class WebSocketService {
  private socket: WebSocket | null = null;
  private readonly url: string;

  constructor(url: string = '') {
    // 使用从config.ts导入的WS_CHAT_ENDPOINT
    this.url = url || WS_CHAT_ENDPOINT;
  }

  connect(handlers: WebSocketHandlers): void {
    if (this.socket) {
      this.disconnect();
    }

    this.socket = new WebSocket(this.url);

    this.socket.onopen = () => {
      console.log('WebSocket connection established');
      if (handlers.onOpen) handlers.onOpen();
    };

    this.socket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        
        // 处理各种类型的消息
        if (data.type === 'thinking' || data.type === 'token' || 
            data.type === 'tool_start' || data.type === 'tool_end' || 
            data.type === 'agent_action' || data.type === 'agent_finish') {
          // 所有思考过程相关的消息都通过onThinking回调处理
          handlers.onThinking(data.content);
        } else if (data.type === 'response') {
          // 最终响应通过onMessage回调处理
          handlers.onMessage(data.content);
        } else if (data.type === 'error') {
          // 错误消息通过onError回调处理
          handlers.onError(data.content);
        }
      } catch (error) {
        console.error('Error parsing WebSocket message:', error);
        handlers.onError('Failed to parse message from server');
      }
    };

    this.socket.onerror = (error) => {
      console.error('WebSocket error:', error);
      handlers.onError('WebSocket connection error');
    };

    this.socket.onclose = () => {
      console.log('WebSocket connection closed');
      if (handlers.onClose) handlers.onClose();
      this.socket = null;
    };
  }

  sendMessage(query: string): void {
    if (!this.socket || this.socket.readyState !== WebSocket.OPEN) {
      throw new Error('WebSocket is not connected');
    }

    this.socket.send(JSON.stringify({ query }));
  }

  disconnect(): void {
    if (this.socket) {
      this.socket.close();
      this.socket = null;
    }
  }

  isConnected(): boolean {
    return this.socket !== null && this.socket.readyState === WebSocket.OPEN;
  }
}

// Create a singleton instance for easy import
const websocketService = new WebSocketService();
export default websocketService;