import React, { useState, useEffect } from 'react';
import { ChatInterface } from './components/ChatInterface';
import { SystemPromptEditor } from './components/SystemPromptEditor';
import { ComplianceDashboard } from './components/ComplianceDashboard';
import { chatApi, complianceApi } from './services/api';
import { SystemPrompt, ChatMessage, ComplianceAnalysis } from './types';

function App() {
  const [systemPrompt, setSystemPrompt] = useState<SystemPrompt>(() => {
    const saved = localStorage.getItem('systemPrompt');
    return saved ? JSON.parse(saved) : {
      content: '',
      guidelines: [],
    };
  });

  const [messages, setMessages] = useState<ChatMessage[]>(() => {
    const saved = localStorage.getItem('chatHistory');
    return saved ? JSON.parse(saved) : [];
  });
  const [isLoading, setIsLoading] = useState(false);
  const [currentAnalysis, setCurrentAnalysis] = useState<ComplianceAnalysis | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  // LLM 모델 선택
  const [llmProvider, setLlmProvider] = useState<string>(() => {
    const saved = localStorage.getItem('llmProvider');
    return saved || 'upstage';
  });
  const [modelName, setModelName] = useState<string>(() => {
    const saved = localStorage.getItem('modelName');
    return saved || '';
  });

  // 시스템 프롬프트 저장
  useEffect(() => {
    localStorage.setItem('systemPrompt', JSON.stringify(systemPrompt));
  }, [systemPrompt]);

  // 대화 히스토리 저장
  useEffect(() => {
    localStorage.setItem('chatHistory', JSON.stringify(messages));
  }, [messages]);

  // LLM 모델 설정 저장
  useEffect(() => {
    localStorage.setItem('llmProvider', llmProvider);
  }, [llmProvider]);

  useEffect(() => {
    localStorage.setItem('modelName', modelName);
  }, [modelName]);

  // 대화 초기화
  const clearHistory = () => {
    setMessages([]);
    setCurrentAnalysis(null);
    localStorage.removeItem('chatHistory');
  };

  const handleSendMessage = async (message: string) => {
    const userMessage: ChatMessage = { role: 'user', content: message };
    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);

    try {
      const response = await chatApi.sendMessage({
        message,
        system_prompt: systemPrompt,
        conversation_history: messages,
        llm_provider: llmProvider || undefined,
        model_name: modelName || undefined,
      });

      const assistantMessage: ChatMessage = {
        role: 'assistant',
        content: response.response,
      };
      setMessages((prev) => [...prev, assistantMessage]);

      // 준수도 분석 가져오기
      setIsAnalyzing(true);
      setTimeout(async () => {
        try {
          const analysis = await complianceApi.getAnalysis(response.compliance_id);
          setCurrentAnalysis(analysis);
        } catch (error) {
          console.error('Failed to fetch compliance analysis:', error);
        } finally {
          setIsAnalyzing(false);
        }
      }, 500);
    } catch (error) {
      console.error('Failed to send message:', error);
      const errorMessage: ChatMessage = {
        role: 'assistant',
        content: '죄송합니다. 메시지 전송 중 오류가 발생했습니다. 서버가 실행 중인지 확인해주세요.',
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div style={styles.app}>
      <header style={styles.header}>
        <h1 style={styles.headerTitle}>System Prompt Compliance Analysis RAG Chatbot</h1>
        <p style={styles.headerSubtitle}>
          Configure system prompts, chat with the bot, and analyze compliance in real-time
        </p>
      </header>

      <div style={styles.container}>
        <div style={styles.leftColumn}>
          {/* LLM 모델 선택 */}
          <div style={styles.modelSelector}>
            <div style={styles.modelSelectorRow}>
              <div style={styles.formGroupInline}>
                <label style={styles.labelInline}>LLM Provider:</label>
                <select
                  value={llmProvider}
                  onChange={(e) => setLlmProvider(e.target.value)}
                  style={styles.selectCompact}
                >
                  <option value="upstage">Upstage Solar</option>
                  <option value="ollama">Ollama</option>
                  <option value="openai">OpenAI</option>
                  <option value="anthropic">Anthropic Claude</option>
                  <option value="gemini">Google Gemini</option>
                </select>
              </div>
              <div style={styles.formGroupInline}>
                <label style={styles.labelInline}>Model Name:</label>
                <input
                  type="text"
                  value={modelName}
                  onChange={(e) => setModelName(e.target.value)}
                  placeholder="Optional"
                  style={styles.inputCompact}
                />
              </div>
            </div>
          </div>

          <SystemPromptEditor
            systemPrompt={systemPrompt}
            onUpdate={setSystemPrompt}
            llmProvider={llmProvider}
            modelName={modelName}
          />
          <ChatInterface
            messages={messages}
            onSendMessage={handleSendMessage}
            isLoading={isLoading}
            onClearHistory={clearHistory}
          />
        </div>

        <div style={styles.rightColumn}>
          <ComplianceDashboard
            analysis={currentAnalysis}
            isLoading={isAnalyzing}
          />
        </div>
      </div>

      <footer style={styles.footer}>
        <p>Powered by Multiple LLM Providers (Upstage, Ollama, OpenAI, Anthropic, Gemini), ChromaDB, FastAPI & React</p>
      </footer>
    </div>
  );
}

const styles: Record<string, React.CSSProperties> = {
  app: {
    minHeight: '100vh',
    backgroundColor: '#f5f5f5',
    display: 'flex',
    flexDirection: 'column',
  },
  header: {
    backgroundColor: '#007bff',
    color: 'white',
    padding: '24px 40px',
    boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
  },
  headerTitle: {
    margin: 0,
    fontSize: '28px',
    fontWeight: 'bold',
  },
  headerSubtitle: {
    margin: '8px 0 0 0',
    fontSize: '14px',
    opacity: 0.9,
  },
  container: {
    flex: 1,
    display: 'grid',
    gridTemplateColumns: '1fr 1fr',
    gap: '24px',
    padding: '24px',
    maxWidth: '1600px',
    margin: '0 auto',
    width: '100%',
  },
  leftColumn: {
    display: 'flex',
    flexDirection: 'column',
    gap: '20px',
  },
  rightColumn: {
    display: 'flex',
    flexDirection: 'column',
  },
  footer: {
    backgroundColor: '#343a40',
    color: 'white',
    textAlign: 'center',
    padding: '16px',
    fontSize: '14px',
  },
  topRow: {
    display: 'flex',
    gap: '16px',
    marginBottom: '20px',
  },
  modelSelector: {
    flex: 1,
    backgroundColor: 'white',
    borderRadius: '8px',
    padding: '12px 16px',
    boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
  },
  modelSelectorRow: {
    display: 'flex',
    gap: '16px',
    alignItems: 'center',
  },
  formGroupInline: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    flex: 1,
  },
  labelInline: {
    fontSize: '13px',
    fontWeight: '500',
    color: '#555',
    whiteSpace: 'nowrap',
  },
  selectCompact: {
    flex: 1,
    padding: '8px 10px',
    fontSize: '13px',
    border: '1px solid #ddd',
    borderRadius: '4px',
    backgroundColor: 'white',
    cursor: 'pointer',
  },
  inputCompact: {
    flex: 1,
    padding: '8px 10px',
    fontSize: '13px',
    border: '1px solid #ddd',
    borderRadius: '4px',
  },
};

export default App;
