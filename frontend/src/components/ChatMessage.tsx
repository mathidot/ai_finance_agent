// frontend/src/components/ChatMessage.tsx
import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm'; // For GitHub Flavored Markdown (tables, etc.)

interface ChatMessageProps {
  message: {
    text: string;
    sender: 'user' | 'agent' | 'thinking';
  };
}

const ChatMessage: React.FC<ChatMessageProps> = ({ message }) => {
  const isUser = message.sender === 'user';
  const isThinking = message.sender === 'thinking';
  const messageClass = isUser ? 'user-message' : isThinking ? 'thinking-message' : 'agent-message';

  return (
    <div className={`message ${messageClass}`}>
      <div className="message-content">
        {/* Use ReactMarkdown to render markdown from the agent */}
      {isThinking ? (
        <div className="thinking-content">
          <div className="thinking-header">Agent's thinking process:</div>
          <ReactMarkdown remarkPlugins={[remarkGfm]}>
            {message.text}
          </ReactMarkdown>
        </div>
      ) : (
        <ReactMarkdown remarkPlugins={[remarkGfm]}>
          {message.text}
        </ReactMarkdown>
      )}
      </div>
    </div>
  );
};

export default ChatMessage;