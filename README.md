# System Prompt Compliance Analysis RAG Chatbot

A real-time system prompt compliance analysis tool that uses RAG (Retrieval-Augmented Generation) and multiple LLM providers to evaluate how well AI responses follow specified guidelines.

## Features

- **Multiple LLM Provider Support**: Seamlessly switch between Upstage Solar, OpenAI, Anthropic Claude, Google Gemini, and Ollama
- **Automatic Guideline Extraction**: Use AI to automatically extract guidelines from system prompts
- **Real-time Compliance Analysis**: Get instant feedback on whether responses follow your guidelines
- **Interactive Dashboard**: Visual compliance scoring with detailed breakdowns
- **RAG Integration**: ChromaDB-powered retrieval for context-aware responses
- **Manual Guideline Management**: Add, remove, and customize guidelines as needed

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

## Troubleshooting

### Backend won't start
- Check if port 8000 is already in use
- Verify all API keys are set in `.env`
- Ensure virtual environment is activated

### Frontend won't start
- Delete `node_modules` and run `npm install` again
- Check if port 3000 is available

### LLM API errors
- Verify your API keys are valid
- Check your API rate limits
- For Ollama: ensure `ollama serve` is running

### ChromaDB errors
- Delete `backend/data/chroma` folder and restart
- Check write permissions in the backend directory

## Repository

GitHub: [https://github.com/jinsoo96/System-Prompt-Compliance](https://github.com/jinsoo96/System-Prompt-Compliance)

## License

MIT License
