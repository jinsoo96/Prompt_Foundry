import axios from 'axios';
import { ChatRequest, ChatResponse, ComplianceAnalysis } from '../types';

const API_BASE_URL = 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const chatApi = {
  sendMessage: async (request: ChatRequest): Promise<ChatResponse> => {
    const response = await api.post<ChatResponse>('/chat/message', request);
    return response.data;
  },

  uploadDocument: async (content: string, metadata?: Record<string, string>) => {
    const response = await api.post('/chat/upload-document', {
      content,
      metadata,
    });
    return response.data;
  },

  extractGuidelines: async (systemPrompt: string, llmProvider?: string, modelName?: string): Promise<string[]> => {
    const response = await api.post<{ guidelines: string[] }>('/chat/extract-guidelines', {
      system_prompt: systemPrompt,
      llm_provider: llmProvider,
      model_name: modelName,
    });
    return response.data.guidelines;
  },
};

export const complianceApi = {
  getAnalysis: async (complianceId: string): Promise<ComplianceAnalysis> => {
    const response = await api.get<ComplianceAnalysis>(`/compliance/${complianceId}`);
    return response.data;
  },
};
