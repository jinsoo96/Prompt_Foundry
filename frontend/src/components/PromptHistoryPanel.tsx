import React from 'react';
import { PromptHistoryResponse } from '../types';

interface Props {
  history: PromptHistoryResponse | null;
  onRefresh: () => void;
}

export const PromptHistoryPanel: React.FC<Props> = ({ history, onRefresh }) => {
  if (!history) {
    return (
      <div style={styles.card}>
        <div style={styles.headerRow}>
          <h3 style={styles.title}>Prompt Versions</h3>
          <button style={styles.refreshButton} onClick={onRefresh}>새로고침</button>
        </div>
        <p style={styles.emptyState}>아직 불러온 프롬프트 버전이 없습니다.</p>
      </div>
    );
  }

  return (
    <div style={styles.card}>
      <div style={styles.headerRow}>
        <h3 style={styles.title}>Prompt Versions</h3>
        <button style={styles.refreshButton} onClick={onRefresh}>새로고침</button>
      </div>
      <div style={styles.list}>
        {history.versions.map((version) => {
          const isCurrent = version.id === history.current_version;
          return (
            <div key={version.id} style={{ ...styles.versionItem, borderColor: isCurrent ? '#007bff' : '#eee' }}>
              <div style={styles.versionHeader}>
                <span style={{ fontWeight: 600 }}>{version.id}</span>
                {isCurrent && <span style={styles.badge}>CURRENT</span>}
              </div>
              <div style={styles.metaRow}>
                <span>{new Date(version.created_at).toLocaleString()}</span>
                {version.score != null && <span>Score: {version.score.toFixed(2)}</span>}
              </div>
              {version.notes && <p style={styles.notes}>{version.notes}</p>}
              <pre style={styles.promptPreview}>{version.content}</pre>
            </div>
          );
        })}
      </div>
    </div>
  );
};

const styles: Record<string, React.CSSProperties> = {
  card: {
    backgroundColor: '#fff',
    borderRadius: '8px',
    padding: '16px',
    boxShadow: '0 2px 4px rgba(0,0,0,0.08)',
    display: 'flex',
    flexDirection: 'column',
    gap: '12px',
  },
  headerRow: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  title: {
    margin: 0,
  },
  refreshButton: {
    padding: '6px 10px',
    borderRadius: '4px',
    border: '1px solid #007bff',
    backgroundColor: '#fff',
    color: '#007bff',
    cursor: 'pointer',
  },
  emptyState: {
    margin: 0,
    color: '#777',
  },
  list: {
    display: 'flex',
    flexDirection: 'column',
    gap: '12px',
    maxHeight: '520px',
    overflowY: 'auto',
  },
  versionItem: {
    border: '1px solid #eee',
    borderRadius: '8px',
    padding: '12px',
    backgroundColor: '#fafafa',
    display: 'flex',
    flexDirection: 'column',
    gap: '6px',
  },
  versionHeader: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
  },
  badge: {
    backgroundColor: '#007bff',
    color: 'white',
    padding: '2px 6px',
    borderRadius: '4px',
    fontSize: '11px',
  },
  metaRow: {
    display: 'flex',
    gap: '12px',
    color: '#666',
    fontSize: '12px',
  },
  notes: {
    margin: 0,
    color: '#444',
    fontSize: '13px',
  },
  promptPreview: {
    backgroundColor: '#fff',
    borderRadius: '4px',
    border: '1px solid #eee',
    padding: '8px',
    maxHeight: '200px',
    overflow: 'auto',
    whiteSpace: 'pre-wrap',
    fontSize: '13px',
  },
};
