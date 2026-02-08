from pydantic import BaseModel
from typing import List, Optional, Dict, Any


class SystemPrompt(BaseModel):
    """시스템 프롬프트 모델"""
    content: str
    guidelines: List[str]  # 구조화된 가이드라인 리스트


class ChatMessage(BaseModel):
    """채팅 메시지 모델"""
    role: str  # 'user' or 'assistant'
    content: str


class ChatRequest(BaseModel):
    """채팅 요청 모델"""
    message: str
    system_prompt: SystemPrompt
    conversation_history: Optional[List[ChatMessage]] = []
    llm_provider: Optional[str] = None  # ollama, openai, upstage, anthropic, gemini
    model_name: Optional[str] = None  # 특정 모델 이름 (선택사항)


class ChatResponse(BaseModel):
    """채팅 응답 모델"""
    response: str
    context_used: List[str]  # RAG에서 사용된 컨텍스트
    compliance_id: str  # 준수도 분석 ID


class GuidelineCompliance(BaseModel):
    """개별 가이드라인 준수 정보"""
    guideline: str
    followed: bool
    explanation: str
    evidence: Optional[str] = None  # 응답에서 해당 부분을 발췌


class ComplianceAnalysis(BaseModel):
    """시스템 프롬프트 준수도 분석 결과"""
    compliance_id: str
    overall_score: float  # 0-100 점수
    guideline_results: List[GuidelineCompliance]
    summary: str


class DocumentUpload(BaseModel):
    """문서 업로드 모델"""
    content: str
    metadata: Optional[Dict[str, str]] = None


class EvaluationRequest(BaseModel):
    """시스템 프롬프트 평가 요청"""
    system_prompt: str
    user_message: str
    model_response: str
    prompt_version: Optional[str] = None
    guidelines: Optional[List[str]] = None
    llm_provider: Optional[str] = None
    model_name: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class MatchedReference(BaseModel):
    """참조 데이터셋 매칭 결과"""
    reference_id: Optional[int]
    similarity_to_chosen: float
    similarity_to_rejected: float
    chosen_preview: Optional[str] = None
    rejected_preview: Optional[str] = None


class EvaluationScores(BaseModel):
    """세부 평가 점수"""
    preference_alignment: float
    guideline_adherence: float
    overall: float


class EvaluationResult(BaseModel):
    """프롬프트 평가 결과"""
    evaluation_id: str
    prompt_version: Optional[str]
    scores: EvaluationScores
    matched_reference: Optional[MatchedReference] = None
    guideline_results: Optional[List[GuidelineCompliance]] = None
    notes: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class PromptVersion(BaseModel):
    """프롬프트 버전 정보"""
    id: str
    content: str
    created_at: str
    score: Optional[float] = None
    notes: Optional[str] = None


class PromptImproveRequest(BaseModel):
    """프롬프트 개선 요청"""
    rationale: Optional[str] = None
    evaluation_ids: Optional[List[str]] = None
    target_score: Optional[float] = None
    run_reevaluation: bool = False


class ReEvaluationResult(BaseModel):
    """자동 재평가 요약"""
    evaluations: List[EvaluationResult]
    summary: Optional[str] = None


class PromptImproveResponse(BaseModel):
    """프롬프트 개선 결과"""
    new_version: PromptVersion
    previous_version: PromptVersion
    message: str
    reevaluation: Optional[ReEvaluationResult] = None


class PromptHistoryResponse(BaseModel):
    """프롬프트 히스토리 응답"""
    current_version: str
    versions: List[PromptVersion]
