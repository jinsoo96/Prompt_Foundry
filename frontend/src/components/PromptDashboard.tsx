import React, { useEffect, useState } from 'react';
import { evaluationApi, promptsApi } from '../services/api';
import {
  PromptHistoryResponse,
  ReEvaluationResult,
  EvaluationResult,
} from '../types';
import { PromptHistoryPanel } from './PromptHistoryPanel';
import { EvaluationList } from './EvaluationList';

export const PromptDashboard: React.FC = () => {
  const [history, setHistory] = useState<PromptHistoryResponse | null>(null);
  const [recentEvaluations, setRecentEvaluations] = useState<EvaluationResult[]>([]);
  const [reevaluation, setReevaluation] = useState<ReEvaluationResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadData = async () => {
    try {
      const [historyData, evaluationData] = await Promise.all([
        promptsApi.getHistory(),
        evaluationApi.getRecent(6),
      ]);
      setHistory(historyData);
      setRecentEvaluations(evaluationData);
    } catch (err) {
      console.error(err);
      setError('데이터를 불러오는 중 문제가 발생했습니다.');
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleImprove = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await promptsApi.improve({ run_reevaluation: true });
      setReevaluation(response.reevaluation || null);
      await loadData();
    } catch (err) {
      console.error(err);
      setError('프롬프트 개선 중 오류가 발생했습니다.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={styles.wrapper}>
      <div style={styles.headerRow}>
        <div>
          <h2 style={{ margin: 0 }}>Prompt Improvement Dashboard</h2>
          <p style={{ margin: '4px 0 0 0', color: '#666', fontSize: '14px' }}>
            프롬프트 버전과 최근 평가 결과를 한눈에 확인하고, 자동 재평가를 실행할 수 있습니다.
          </p>
        </div>
        <button style={styles.primaryButton} onClick={handleImprove} disabled={loading}>
          {loading ? '개선 중…' : '자동 개선 + 재평가'}
        </button>
      </div>

      {error && <div style={styles.error}>{error}</div>}

      <div style={styles.grid}>
        <PromptHistoryPanel history={history} onRefresh={loadData} />
        <div style={styles.sideColumn}>
          <EvaluationList evaluations={recentEvaluations} title="Recent Evaluations" />
          {reevaluation && (
            <div style={styles.card}>
              <h3 style={{ marginTop: 0 }}>Re-evaluation Summary</h3>
              <p style={{ margin: '8px 0', color: '#333' }}>{reevaluation.summary}</p>
              <EvaluationList evaluations={reevaluation.evaluations} title="Latest Re-evaluation" />
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

const styles: Record<string, React.CSSProperties> = {
  wrapper: {
    display: 'flex',
    flexDirection: 'column',
    gap: '16px',
  },
  headerRow: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    backgroundColor: '#fff',
    borderRadius: '8px',
    padding: '16px',
    boxShadow: '0 2px 4px rgba(0,0,0,0.08)',
  },
  primaryButton: {
    backgroundColor: '#007bff',
    border: 'none',
    color: '#fff',
    padding: '10px 16px',
    borderRadius: '6px',
    cursor: 'pointer',
    fontWeight: 600,
  },
  error: {
    backgroundColor: '#f8d7da',
    color: '#842029',
    padding: '10px 12px',
    borderRadius: '6px',
  },
  grid: {
    display: 'grid',
    gridTemplateColumns: '2fr 1fr',
    gap: '20px',
  },
  sideColumn: {
    display: 'flex',
    flexDirection: 'column',
    gap: '12px',
  },
  card: {
    backgroundColor: '#fff',
    borderRadius: '8px',
    padding: '12px',
    boxShadow: '0 2px 4px rgba(0,0,0,0.08)',
  },
};
