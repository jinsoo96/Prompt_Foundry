export interface SystemPrompt {
  content: string;
  guidelines: string[];
}

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

export interface ChatRequest {
  message: string;
  system_prompt: SystemPrompt;
  conversation_history?: ChatMessage[];
  llm_provider?: string;
  model_name?: string;
}

export interface ChatResponse {
  response: string;
  context_used: string[];
  compliance_id: string;
}

export interface GuidelineCompliance {
  guideline: string;
  followed: boolean;
  explanation: string;
  evidence?: string;
}

export interface ComplianceAnalysis {
  compliance_id: string;
  overall_score: number;
  guideline_results: GuidelineCompliance[];
  summary: string;
}
