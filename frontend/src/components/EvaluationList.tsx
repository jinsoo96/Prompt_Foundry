import React from 'react';
import { EvaluationResult } from '../types';

interface Props {
  evaluations: EvaluationResult[];
  title?: string;
}

export const EvaluationList: React.FC<Props> = ({ evaluations, title = 'Recent Evaluations' }) => (
  <div style={styles.card}>
    <h3 style={styles.title}>{title}</h3>
    {evaluations.length === 0 ? (
      <p style={styles.empty}>아직 평가 데이터가 없습니다.</p>
    ) : (
      <div style={styles.list}>
        {evaluations.map((evaluation) => (
          <div key={evaluation.evaluation_id} style={styles.item}>
            <div style={styles.itemHeader}>
              <strong>{evaluation.prompt_version || '—'}</strong>
              <span>Overall {evaluation.scores.overall.toFixed(3)}</span>
            </div>
            <div style={styles.scoreRow}>
              <span>Pref: {evaluation.scores.preference_alignment.toFixed(3)}</span>
              <span>Guideline: {evaluation.scores.guideline_adherence.toFixed(3)}</span>
            </div>
            {evaluation.guideline_results && evaluation.guideline_results.length > 0 && (
              <ul style={styles.guidelineList}>
                {evaluation.guideline_results.slice(0, 3).map((result, idx) => (
                  <li key={idx} style={{ color: result.followed ? '#157347' : '#b02a37' }}>
                    {result.followed ? '✅' : '⚠️'} {result.guideline}
                  </li>
                ))}
              </ul>
            )}
          </div>
        ))}
      </div>
    )}
  </div>
);

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
  title: {
    margin: 0,
  },
  empty: {
    margin: 0,
    color: '#777',
  },
  list: {
    display: 'flex',
    flexDirection: 'column',
    gap: '12px',
  },
  item: {
    border: '1px solid #eee',
    borderRadius: '8px',
    padding: '10px 12px',
    backgroundColor: '#fafafa',
    display: 'flex',
    flexDirection: 'column',
    gap: '6px',
  },
  itemHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    color: '#333',
  },
  scoreRow: {
    display: 'flex',
    gap: '12px',
    fontSize: '13px',
    color: '#555',
  },
  guidelineList: {
    margin: 0,
    paddingLeft: '18px',
    fontSize: '13px',
  },
};
