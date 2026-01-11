from pydantic import BaseModel
from typing import List, Optional, Dict


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
