// frontend/src/services/config.ts

// 定义API基础URL
export const API_BASE_URL = 'http://localhost:3000';

// 构建WebSocket URL
export const WS_BASE_URL = API_BASE_URL.replace(/^http/, 'ws');
export const WS_CHAT_ENDPOINT = `${WS_BASE_URL}/ws/chat`;