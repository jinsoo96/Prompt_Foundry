# System Prompt Compliance Analysis RAG Chatbot

시스템 프롬프트에 대한 준수도를 분석하는 RAG 기반 챗봇입니다. 여러 LLM 프로바이더를 지원하며, AI 응답이 지정된 가이드라인을 얼마나 잘 따르는지 평가합니다.

## Features

- 다양한 LLM 프로바이더 지원 (Upstage Solar, OpenAI, Anthropic Claude, Google Gemini, Ollama)
- AI 기반 자동 가이드라인 추출
- 실시간 준수도 분석 및 스코어링
- ChromaDB 기반 RAG 통합
- 수동 가이드라인 관리
- 수동/자동 프롬프트 버전 관리 및 재평가 대시보드

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend (React)                      │
│  ┌──────────────────┐  ┌──────────────────┐  ┌────────────┐│
│  │  System Prompt   │  │   RAG Chatbot    │  │ Compliance ││
│  │     Editor       │  │   Interface      │  │ Dashboard  ││
│  └──────────────────┘  └──────────────────┘  └────────────┘│
└─────────────────────────────────────────────────────────────┘
                              │
                              │ HTTP/REST API
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     Backend (FastAPI)                        │
│  ┌──────────────────────────────────────────────────────┐   │
│  │                   API Routes                          │   │
│  │  /api/chat/message                                    │   │
│  │  /api/chat/extract-guidelines                         │   │
│  │  /api/compliance/{id}                                 │   │
│  └──────────────────────────────────────────────────────┘   │
│                              │                               │
│       ┌──────────────────────┼──────────────────────┐       │
│       ▼                      ▼                      ▼       │
│  ┌─────────┐         ┌──────────────┐      ┌──────────┐    │
│  │   RAG   │         │  Compliance  │      │   LLM    │    │
│  │ Service │         │   Checker    │      │ Provider │    │
│  └─────────┘         └──────────────┘      └──────────┘    │
│       │                                           │         │
│       ▼                                           │         │
│  ┌─────────┐                                      │         │
│  │ChromaDB │                                      │         │
│  │ Vector  │                                      │         │
│  │   DB    │                                      │         │
│  └─────────┘                                      │         │
└───────────────────────────────────────────────────┼─────────┘
                                                    │
                    ┌───────────────────────────────┼─────────────────┐
                    ▼                               ▼                 ▼
            ┌───────────────┐            ┌──────────────┐   ┌──────────────┐
            │ Upstage Solar │            │   OpenAI     │   │  Anthropic   │
            │  (Default)    │            │              │   │    Claude    │
            └───────────────┘            └──────────────┘   └──────────────┘
                    ▼                               ▼                 ▼
            ┌───────────────┐            ┌──────────────┐
            │    Ollama     │            │Google Gemini │
            │               │            │              │
            └───────────────┘            └──────────────┘
```

## Tech Stack

### Frontend
- **React** with TypeScript
- **Vite** for fast development
- **Recharts** for compliance visualization
- **Axios** for API communication

### Backend
- **FastAPI** for high-performance REST API
- **ChromaDB** for vector storage and RAG
- **SQLite** (`backend/data/app.db`) for prompt/evaluation persistence
- **Sentence Transformers** for embeddings
- **Pydantic** for data validation
- **Multiple LLM Providers**:
  - Upstage Solar API
  - OpenAI API
  - Anthropic Claude API
  - Google Gemini API
  - Ollama (local)

## Installation

### Prerequisites
- Python 3.11+
- Node.js 18+
- npm

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Create a `.env` file in the `backend` directory:

```env
# LLM Provider (ollama, openai, upstage, anthropic, gemini)
LLM_PROVIDER=upstage

# Ollama (if using LLM_PROVIDER=ollama)
OLLAMA_MODEL=llama3.2
OLLAMA_HOST=http://localhost:11434

# OpenAI (if using LLM_PROVIDER=openai)
OPENAI_API_KEY=your-openai-api-key
OPENAI_MODEL=gpt-3.5-turbo

# Upstage Solar (if using LLM_PROVIDER=upstage)
UPSTAGE_API_KEY=your-upstage-api-key
UPSTAGE_MODEL=solar-pro2

# Anthropic (if using LLM_PROVIDER=anthropic)
ANTHROPIC_API_KEY=your-anthropic-api-key
ANTHROPIC_MODEL=claude-3-haiku-20240307

# Google Gemini (if using LLM_PROVIDER=gemini)
GOOGLE_API_KEY=your-google-api-key
GEMINI_MODEL=gemini-1.5-flash

# ChromaDB
CHROMA_DB_PATH=./data/chroma

# API
API_HOST=0.0.0.0
API_PORT=8000
```

### Frontend Setup

```bash
cd frontend
npm install
```

## Running the Application

### Option 1: Start All Services (Recommended)

```bash
./start-all.sh
```

This will:
- Start the backend server on http://localhost:8000
- Start the frontend server on http://localhost:3000
- Automatically open your browser
- Display real-time logs

### Option 2: Manual Start

**Backend:**
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend:**
```bash
cd frontend
npm run dev
```

## Usage

1. **Select LLM Provider**: Choose your preferred LLM from the dropdown (Upstage, OpenAI, etc.)

2. **Configure System Prompt**:
   - Enter your system prompt in the text area
   - Click "LLM Guidelines Extraction" to automatically extract guidelines
   - Or manually add guidelines using the "+ Add Manually" button

3. **Chat with the Bot**:
   - Type your message in the chat interface
   - The AI will respond based on your system prompt

4. **View Compliance Analysis**:
   - See real-time compliance scoring
   - Review detailed analysis for each guideline
   - Check which guidelines were followed/not followed with evidence

5. **Improve + Re-evaluate Prompts**:
   - 우측 패널의 “자동 개선 + 재평가” 버튼을 누르면 `/api/prompts/improve`가 호출되어 새로운 시스템 프롬프트 버전을 생성하고, 기본 시나리오 4종(불법 요청 거절, 개인정보 요청 거절, 매출 인사이트 요약, CS 보고서 톤)을 자동 재평가합니다.
   - 생성된 버전과 재평가 결과는 Prompt Dashboard에서 즉시 확인할 수 있습니다.

## API Documentation

Once the backend is running, visit:
- API Docs: http://localhost:8000/docs
- Alternative Docs: http://localhost:8000/redoc

### Key Endpoints

- `POST /api/chat/message` - Send a chat message and get compliance analysis
- `POST /api/chat/extract-guidelines` - Extract guidelines from system prompt using LLM
- `GET /api/compliance/{compliance_id}` - Get detailed compliance analysis
- `POST /api/chat/upload-document` - Upload documents to RAG knowledge base

## Project Structure

```
prompt-compliance-rag/
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPI application entry point
│   │   ├── dependencies.py         # Dependency injection
│   │   ├── models/
│   │   │   └── schemas.py          # Pydantic models
│   │   ├── routes/
│   │   │   ├── chat.py            # Chat and guideline endpoints
│   │   │   └── compliance.py      # Compliance analysis endpoints
│   │   └── services/
│   │       ├── compliance_checker.py  # Compliance analysis logic
│   │       ├── llm_provider.py        # Multi-LLM abstraction
│   │       └── rag_service.py         # RAG with ChromaDB
│   ├── requirements.txt
│   └── .env
├── frontend/
│   ├── src/
│   │   ├── App.tsx                # Main application component
│   │   ├── components/
│   │   │   ├── ChatInterface.tsx
│   │   │   ├── ComplianceDashboard.tsx
│   │   │   └── SystemPromptEditor.tsx
│   │   ├── services/
│   │   │   └── api.ts             # API client
│   │   └── types/
│   │       └── index.ts           # TypeScript types
│   ├── package.json
│   └── vite.config.ts
├── start-all.sh                   # Convenience script to start all services
└── README.md
```

## Configuration

### Switching LLM Providers

You can switch LLM providers in two ways:

1. **Environment Variable** (default for all requests):
   Edit `backend/.env` and change `LLM_PROVIDER`

2. **Per-Request** (runtime selection):
   Use the LLM provider dropdown in the UI

### Adding Custom Documents to RAG

Use the `/api/chat/upload-document` endpoint:

```bash
curl -X POST http://localhost:8000/api/chat/upload-document \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Your document content here",
    "metadata": {"source": "custom"}
  }'
```

## Automatic Prompt Improvement

- **Version Store**: 모든 프롬프트 버전은 SQLite(`backend/data/app.db`)에 저장되며, `/api/prompts/history`로 확인할 수 있습니다.
- **개선 API**: `POST /api/prompts/improve` 에 `run_reevaluation: true`를 포함하면 시나리오 전체 자동 재평가가 실행되어 `reevaluation` 필드로 결과가 반환됩니다.
- **시나리오 구성** (`backend/app/config/scenarios.json`):
  1. Safety refusal (불법 행위 거절)
  2. PII refusal (개인정보 요청 거절)
  3. Data insight summary (매출 데이터 요약 + 원인 분석)
  4. Customer-service report tone (CS 보고서 이슈/원인/조치)

## Experiment Playbook

1. **서비스 기동**: `./start-all.sh` 실행 후 http://localhost:8000, http://localhost:3000 접속.
2. **프롬프트 편집**: 좌측 System Prompt Editor에서 도메인 지침 입력 → 가이드라인 추출 버튼으로 구조화.
3. **대화/준수도 확인**: Chat 패널에서 메시지 전송 → 준수도 대시보드로 즉시 스코어 확인.
4. **자동 개선 실험**: 프롬트 대시보드 '자동 개선 + 재평가' 버튼 클릭 또는 `curl -X POST http://localhost:8000/api/prompts/improve -H 'Content-Type: application/json' -d '{\"run_reevaluation\": true}'`.
5. **결과 분석**: Prompt Dashboard 카드 혹은 `GET /api/evaluation/recent?limit=6`으로 최근 평가 확인.
6. **시나리오 확장**: `app/config/scenarios.json`에 추가 시나리오 정의 → 서버 재시작.


## License

Copyright (c) 2026 jinsoo96. All rights reserved.
