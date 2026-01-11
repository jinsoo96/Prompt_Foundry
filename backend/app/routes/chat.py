from fastapi import APIRouter, HTTPException
from app.models.schemas import ChatRequest, ChatResponse, DocumentUpload
from app.dependencies import rag_service, compliance_checker
import uuid

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("/message", response_model=ChatResponse)
async def send_message(request: ChatRequest):
    """채팅 메시지 전송 및 응답 생성"""
    try:
        # RAG 챗봇으로 응답 생성
        result = rag_service.chat(
            message=request.message,
            system_prompt=request.system_prompt.content,
            conversation_history=[
                {"role": msg.role, "content": msg.content}
                for msg in request.conversation_history
            ] if request.conversation_history else None,
            llm_provider=request.llm_provider,
            model_name=request.model_name
        )

        # 준수도 분석
        compliance_analysis = compliance_checker.analyze_compliance(
            system_prompt_guidelines=request.system_prompt.guidelines,
            user_message=request.message,
            assistant_response=result["response"],
            llm_provider=request.llm_provider,
            model_name=request.model_name
        )

        return ChatResponse(
            response=result["response"],
            context_used=result["context_used"],
            compliance_id=compliance_analysis.compliance_id
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload-document")
async def upload_document(doc: DocumentUpload):
    """문서를 RAG 시스템에 업로드"""
    try:
        # 문서를 청크로 나누기 (간단한 예제)
        chunks = [doc.content[i:i+500] for i in range(0, len(doc.content), 500)]

        # 메타데이터 설정
        metadatas = [doc.metadata or {} for _ in chunks]

        # 문서 추가
        ids = rag_service.add_documents(chunks, metadatas)

        return {
            "message": "Document uploaded successfully",
            "chunks_added": len(ids)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/extract-guidelines")
async def extract_guidelines(request: dict):
    """시스템 프롬프트에서 가이드라인 자동 추출 (LLM 기반)"""
    try:
        system_prompt = request.get("system_prompt", "")
        if not system_prompt:
            raise HTTPException(status_code=400, detail="system_prompt is required")

        llm_provider = request.get("llm_provider", "upstage")
        model_name = request.get("model_name")

        guidelines = compliance_checker.extract_guidelines(
            system_prompt,
            llm_provider=llm_provider,
            model_name=model_name
        )

        return {
            "guidelines": guidelines
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
