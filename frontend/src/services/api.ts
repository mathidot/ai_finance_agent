// frontend/src/services/api.ts
import { API_BASE_URL } from './config';

interface ChatResponse {
  response: string;
  error?: string;
}

export const sendMessage = async (query: string): Promise<ChatResponse> => {
  try {
    const response = await fetch(`${API_BASE_URL}/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ query }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Failed to get response from agent.');
    }

    const data: ChatResponse = await response.json();
    return data;
  } catch (error) {
    console.error('API call error:', error);
    throw error;
  }
};