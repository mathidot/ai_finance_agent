// frontend/src/App.tsx
import React, { useState, useEffect, useRef } from 'react';
import './App.css'; // Optional: for basic styling
import { sendMessage } from './services/api'; // Import the API service
import websocketService from './services/websocket'; // Import WebSocket service
import ChatMessage from './components/ChatMessage'; // Import ChatMessage component

interface Message {
  id: number;
  text: string;
  sender: 'user' | 'agent' | 'thinking';
}

function App() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);
  const [thinking, setThinking] = useState<string>('');
  const [useWebSocket, setUseWebSocket] = useState<boolean>(true);
  const messagesEndRef = useRef<HTMLDivElement>(null); // For auto-scrolling
  const thinkingMessageId = useRef<number | null>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(scrollToBottom, [messages, thinking]);
  
  // Setup WebSocket connection
  useEffect(() => {
    if (useWebSocket) {
      websocketService.connect({
        onMessage: (response) => {
          // When final response is received
          if (thinkingMessageId.current !== null) {
            // Remove the thinking message
            setMessages(prevMessages => 
              prevMessages.filter(msg => msg.id !== thinkingMessageId.current)
            );
            thinkingMessageId.current = null;
          }
          
          // Add the final agent response
          const agentMessage: Message = { 
            id: Date.now(), 
            text: response, 
            sender: 'agent' 
          };
          setMessages(prevMessages => [...prevMessages, agentMessage]);
          setLoading(false);
          setThinking('');
        },
        onThinking: (thinkingText) => {
          // 更新思考文本状态
          setThinking(prevThinking => {
            // 对于新的思考步骤，添加换行符
            const newThinking = prevThinking ? `${prevThinking}\n${thinkingText}` : thinkingText;
            return newThinking;
          });
          
          // 如果还没有思考消息，创建一个新的
          if (thinkingMessageId.current === null) {
            const newId = Date.now();
            thinkingMessageId.current = newId;
            const thinkingMessage: Message = { 
              id: newId, 
              text: thinkingText, 
              sender: 'thinking' 
            };
            setMessages(prevMessages => [...prevMessages, thinkingMessage]);
          } else {
            // 更新现有的思考消息，保留所有思考步骤
            setMessages(prevMessages => 
              prevMessages.map(msg => 
                msg.id === thinkingMessageId.current 
                  ? { ...msg, text: msg.text + '\n' + thinkingText }
                  : msg
              )
            );
          }
        },
        onError: (error) => {
          console.error('WebSocket error:', error);
          setLoading(false);
          const errorMessage: Message = {
            id: Date.now(),
            text: 'Sorry, something went wrong with the connection. Please try again.',
            sender: 'agent',
          };
          setMessages(prevMessages => [...prevMessages, errorMessage]);
        },
        onOpen: () => console.log('WebSocket connected'),
        onClose: () => console.log('WebSocket disconnected')
      });
    }
    
    return () => {
      if (useWebSocket) {
        websocketService.disconnect();
      }
    };
  }, [useWebSocket]);

  const handleSendMessage = async () => {
    if (inputMessage.trim() === '') return;

    const userMessage: Message = { id: Date.now(), text: inputMessage, sender: 'user' };
    setMessages((prevMessages) => [...prevMessages, userMessage]);
    setInputMessage('');
    setLoading(true);
    
    // Reset thinking state
    setThinking('');
    thinkingMessageId.current = null;

    if (useWebSocket && websocketService.isConnected()) {
      // Send via WebSocket for streaming response
      try {
        websocketService.sendMessage(inputMessage);
        // The response will be handled by the WebSocket callbacks
      } catch (error) {
        console.error('Error sending WebSocket message:', error);
        fallbackToRestApi(inputMessage);
      }
    } else {
      // Fallback to REST API
      fallbackToRestApi(inputMessage);
    }
  };
  
  const fallbackToRestApi = async (query: string) => {
    try {
      const response = await sendMessage(query);
      const agentMessage: Message = { id: Date.now() + 1, text: response.response, sender: 'agent' };
      setMessages((prevMessages) => [...prevMessages, agentMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage: Message = {
        id: Date.now() + 1,
        text: 'Sorry, something went wrong. Please try again.',
        sender: 'agent',
      };
      setMessages((prevMessages) => [...prevMessages, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !loading) {
      handleSendMessage();
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Qwen Finance Agent Chat</h1>
        <div className="toggle-container">
          <label>
            <input
              type="checkbox"
              checked={useWebSocket}
              onChange={() => setUseWebSocket(!useWebSocket)}
            />
            Show thinking process
          </label>
        </div>
      </header>
      <main className="chat-container">
        <div className="messages-display">
          {messages.map((msg) => (
            <ChatMessage key={msg.id} message={msg} />
          ))}
          {loading && !useWebSocket && (
            <div className="message agent-message thinking">
              <span>Agent is thinking...</span>
            </div>
          )}
          <div ref={messagesEndRef} /> {/* Scroll target */}
        </div>
        <div className="input-area">
          <input
            type="text"
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask me about stocks (e.g., 'What is AAPL stock price?')"
            disabled={loading}
          />
          <button onClick={handleSendMessage} disabled={loading}>
            Send
          </button>
        </div>
      </main>
    </div>
  );
}

export default App;