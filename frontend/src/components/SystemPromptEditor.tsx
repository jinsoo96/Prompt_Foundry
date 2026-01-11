import React, { useState } from 'react';
import { SystemPrompt } from '../types';
import { chatApi } from '../services/api';

interface SystemPromptEditorProps {
  systemPrompt: SystemPrompt;
  onUpdate: (prompt: SystemPrompt) => void;
  llmProvider: string;
  modelName: string;
}

export const SystemPromptEditor: React.FC<SystemPromptEditorProps> = ({
  systemPrompt,
  onUpdate,
  llmProvider,
  modelName,
}) => {
  const [content, setContent] = useState(systemPrompt.content);
  const [isExtracting, setIsExtracting] = useState(false);

  const handleContentChange = (newContent: string) => {
    setContent(newContent);
    onUpdate({ ...systemPrompt, content: newContent });
  };

  // LLM을 사용하여 시스템 프롬프트에서 가이드라인 자동 추출
  const extractGuidelines = async () => {
    if (!content.trim()) return;

    setIsExtracting(true);
    try {
      const extracted = await chatApi.extractGuidelines(content, llmProvider, modelName || undefined);

      if (extracted.length > 0) {
        // 기존 가이드라인을 덮어쓰고 새로 추출한 것만 사용
        onUpdate({ ...systemPrompt, content, guidelines: extracted });
      }
    } catch (error) {
      console.error('Failed to extract guidelines:', error);
      alert('Failed to extract guidelines. Please check if the server is running.');
    } finally {
      setIsExtracting(false);
    }
  };

  const handleRemoveGuideline = (index: number) => {
    const updated = systemPrompt.guidelines.filter((_, i) => i !== index);
    onUpdate({ ...systemPrompt, guidelines: updated });
  };

  const handleAddGuideline = () => {
    const newGuideline = prompt('Enter a new guideline:');
    if (newGuideline && newGuideline.trim()) {
      const updated = [...systemPrompt.guidelines, newGuideline.trim()];
      onUpdate({ ...systemPrompt, guidelines: updated });
    }
  };

  return (
    <div style={styles.container}>
      <h2 style={styles.title}>System Prompt Settings</h2>

      <div style={styles.section}>
        <label style={styles.label}>Prompt Content</label>
        <textarea
          value={content}
          onChange={(e) => handleContentChange(e.target.value)}
          style={styles.textarea}
          placeholder="Enter your system prompt..."
          rows={6}
        />
        <button
          onClick={extractGuidelines}
          style={{
            ...styles.extractButton,
            opacity: isExtracting ? 0.7 : 1,
            cursor: isExtracting ? 'not-allowed' : 'pointer',
          }}
          disabled={isExtracting}
        >
          {isExtracting ? 'Extracting...' : 'LLM Guidelines Extraction'}
        </button>
      </div>

      <div style={styles.section}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '20px' }}>
          <label style={styles.label}>Guidelines ({systemPrompt.guidelines.length})</label>
          <button onClick={handleAddGuideline} style={styles.addButton}>
            + Add Manually
          </button>
        </div>
        {systemPrompt.guidelines.length > 0 ? (
          <ul style={styles.guidelineList}>
            {systemPrompt.guidelines.map((guideline, index) => (
              <li key={index} style={styles.guidelineItem}>
                <span style={styles.guidelineText}>{guideline}</span>
                <button
                  onClick={() => handleRemoveGuideline(index)}
                  style={styles.removeButton}
                >
                  ✕
                </button>
              </li>
            ))}
          </ul>
        ) : (
          <p style={styles.emptyText}>No guidelines yet. Extract with AI or add manually.</p>
        )}
      </div>
    </div>
  );
};

const styles: Record<string, React.CSSProperties> = {
  container: {
    padding: '20px',
    backgroundColor: '#f9f9f9',
    borderRadius: '8px',
  },
  title: {
    fontSize: '20px',
    fontWeight: 'bold',
    marginBottom: '16px',
  },
  section: {
    marginBottom: '0',
  },
  label: {
    display: 'block',
    fontWeight: '600',
    marginBottom: '8px',
    fontSize: '14px',
  },
  textarea: {
    width: '100%',
    padding: '10px',
    fontSize: '14px',
    border: '1px solid #ddd',
    borderRadius: '4px',
    fontFamily: 'inherit',
    resize: 'vertical',
  },
  extractButton: {
    marginTop: '8px',
    padding: '8px 16px',
    backgroundColor: '#28a745',
    color: 'white',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer',
    fontSize: '13px',
  },
  addButton: {
    padding: '6px 12px',
    backgroundColor: '#007bff',
    color: 'white',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer',
    fontSize: '12px',
  },
  guidelineList: {
    listStyle: 'none',
    padding: 0,
    margin: '8px 0 0 0',
  },
  guidelineItem: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '10px 12px',
    backgroundColor: 'white',
    border: '1px solid #ddd',
    borderRadius: '4px',
    marginBottom: '8px',
  },
  guidelineText: {
    flex: 1,
    fontSize: '13px',
    color: '#333',
  },
  removeButton: {
    padding: '4px 8px',
    backgroundColor: '#dc3545',
    color: 'white',
    border: 'none',
    borderRadius: '3px',
    cursor: 'pointer',
    fontSize: '12px',
    marginLeft: '8px',
  },
  emptyText: {
    fontSize: '13px',
    color: '#999',
    fontStyle: 'italic',
    marginTop: '8px',
  },
};
