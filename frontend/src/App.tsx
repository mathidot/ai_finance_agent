// frontend/src/App.tsx
import React, { useState, useEffect, useRef } from 'react';
import './App.css'; // Optional: for basic styling
import { sendMessage } from './services/api'; // Import the API service
import ChatMessage from './components/ChatMessage'; // Import ChatMessage component

interface Message {
  id: number;
  text: string;
  sender: 'user' | 'agent';
}

function App() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);
  const messagesEndRef = useRef<HTMLDivElement>(null); // For auto-scrolling

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(scrollToBottom, [messages]);

  const handleSendMessage = async () => {
    if (inputMessage.trim() === '') return;

    const userMessage: Message = { id: Date.now(), text: inputMessage, sender: 'user' };
    setMessages((prevMessages) => [...prevMessages, userMessage]);
    setInputMessage('');
    setLoading(true);

    try {
      const response = await sendMessage(inputMessage);
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
      </header>
      <main className="chat-container">
        <div className="messages-display">
          {messages.map((msg) => (
            <ChatMessage key={msg.id} message={msg} />
          ))}
          {loading && (
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