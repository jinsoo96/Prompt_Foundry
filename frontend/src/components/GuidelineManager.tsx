import React, { useState } from 'react';

interface GuidelineManagerProps {
  guidelines: string[];
  onUpdate: (guidelines: string[]) => void;
}

export const GuidelineManager: React.FC<GuidelineManagerProps> = ({
  guidelines,
  onUpdate,
}) => {
  const [newGuideline, setNewGuideline] = useState('');

  const handleAddGuideline = () => {
    if (newGuideline.trim()) {
      const updated = [...guidelines, newGuideline.trim()];
      onUpdate(updated);
      setNewGuideline('');
    }
  };

  const handleRemoveGuideline = (index: number) => {
    const updated = guidelines.filter((_, i) => i !== index);
    onUpdate(updated);
  };

  return (
    <div style={styles.container}>
      <label style={styles.label}>가이드라인 ({guidelines.length}개)</label>

      <div style={styles.guidelineInput}>
        <input
          type="text"
          value={newGuideline}
          onChange={(e) => setNewGuideline(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleAddGuideline()}
          placeholder="새 가이드라인..."
          style={styles.input}
        />
        <button onClick={handleAddGuideline} style={styles.addButton}>
          추가
        </button>
      </div>

      <div style={styles.guidelineListContainer}>
        {guidelines.map((guideline, index) => (
          <div key={index} style={styles.guidelineItem}>
            <span style={styles.guidelineText}>{guideline}</span>
            <button
              onClick={() => handleRemoveGuideline(index)}
              style={styles.removeButton}
            >
              삭제
            </button>
          </div>
        ))}
      </div>
    </div>
  );
};

const styles: Record<string, React.CSSProperties> = {
  container: {
    flex: 1,
    backgroundColor: 'white',
    borderRadius: '8px',
    padding: '12px 16px',
    boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
    display: 'flex',
    flexDirection: 'column',
  },
  label: {
    fontSize: '13px',
    fontWeight: '600',
    marginBottom: '8px',
    color: '#555',
  },
  guidelineInput: {
    display: 'flex',
    gap: '8px',
    marginBottom: '8px',
  },
  input: {
    flex: 1,
    padding: '8px 10px',
    fontSize: '13px',
    border: '1px solid #ddd',
    borderRadius: '4px',
  },
  addButton: {
    padding: '8px 16px',
    backgroundColor: '#007bff',
    color: 'white',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer',
    fontSize: '13px',
    whiteSpace: 'nowrap',
  },
  guidelineListContainer: {
    display: 'flex',
    flexDirection: 'column',
    gap: '6px',
    maxHeight: '150px',
    overflowY: 'auto',
  },
  guidelineItem: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '6px 10px',
    backgroundColor: '#f8f9fa',
    border: '1px solid #e0e0e0',
    borderRadius: '4px',
    fontSize: '12px',
  },
  guidelineText: {
    flex: 1,
    marginRight: '8px',
  },
  removeButton: {
    padding: '3px 10px',
    backgroundColor: '#dc3545',
    color: 'white',
    border: 'none',
    borderRadius: '3px',
    cursor: 'pointer',
    fontSize: '11px',
    whiteSpace: 'nowrap',
  },
};
