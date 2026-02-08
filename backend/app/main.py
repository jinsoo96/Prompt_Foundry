from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import chat, compliance, evaluation, prompt

app = FastAPI(
    title="Prompt Compliance RAG API",
    description="시스템 프롬프트 준수도를 분석하는 RAG 챗봇 API",
    version="1.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # React 개발 서버
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(chat.router)
app.include_router(compliance.router)
app.include_router(evaluation.router)
app.include_router(prompt.router)


@app.get("/")
async def root():
    return {
        "message": "Prompt Compliance RAG API",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
