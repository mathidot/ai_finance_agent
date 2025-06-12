// frontend/src/components/ChatMessage.tsx
import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm'; // For GitHub Flavored Markdown (tables, etc.)
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';

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

  // 自定义组件用于代码块语法高亮
  const components = {
    code({ node, inline, className, children, ...props }: any) {
      const match = /language-(\w+)/.exec(className || '');
      return !inline && match ? (
        <SyntaxHighlighter
          style={vscDarkPlus}
          language={match[1]}
          PreTag="div"
          {...props}
        >
          {String(children).replace(/\n$/, '')}
        </SyntaxHighlighter>
      ) : (
        <code className={className} {...props}>
          {children}
        </code>
      );
    },
    // 自定义表格样式
    table({ node, ...props }: any) {
      return (
        <div className="table-container">
          <table className="markdown-table" {...props} />
        </div>
      );
    }
  };

  return (
    <div className={`message ${messageClass}`}>
      <div className="message-content">
        {isThinking ? (
          <div className="thinking-content">
            <div className="thinking-header">Agent's thinking process:</div>
            <ReactMarkdown 
              remarkPlugins={[remarkGfm]}
              components={components}
            >
              {message.text}
            </ReactMarkdown>
          </div>
        ) : (
          <ReactMarkdown 
            remarkPlugins={[remarkGfm]}
            components={components}
          >
            {message.text}
          </ReactMarkdown>
        )}
      </div>
    </div>
  );
};

export default ChatMessage;