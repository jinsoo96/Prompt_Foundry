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

export interface PromptVersion {
  id: string;
  content: string;
  created_at: string;
  score?: number | null;
  notes?: string | null;
}

export interface PromptHistoryResponse {
  current_version: string;
  versions: PromptVersion[];
}

export interface EvaluationScores {
  preference_alignment: number;
  guideline_adherence: number;
  overall: number;
}

export interface MatchedReference {
  reference_id?: number | null;
  similarity_to_chosen: number;
  similarity_to_rejected: number;
  chosen_preview?: string | null;
  rejected_preview?: string | null;
}

export interface EvaluationResult {
  evaluation_id: string;
  prompt_version?: string | null;
  scores: EvaluationScores;
  matched_reference?: MatchedReference | null;
  guideline_results?: GuidelineCompliance[] | null;
  notes?: string | null;
  metadata?: Record<string, any> | null;
}

export interface ReEvaluationResult {
  evaluations: EvaluationResult[];
  summary?: string;
}

export interface PromptImproveRequest {
  rationale?: string;
  evaluation_ids?: string[];
  target_score?: number;
  run_reevaluation?: boolean;
}

export interface PromptImproveResponse {
  new_version: PromptVersion;
  previous_version: PromptVersion;
  message: string;
  reevaluation?: ReEvaluationResult | null;
}
