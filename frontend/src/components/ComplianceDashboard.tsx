import React from 'react';
import { ComplianceAnalysis } from '../types';
import { PieChart, Pie, Cell, ResponsiveContainer, Legend } from 'recharts';

interface ComplianceDashboardProps {
  analysis: ComplianceAnalysis | null;
  isLoading: boolean;
}

export const ComplianceDashboard: React.FC<ComplianceDashboardProps> = ({
  analysis,
  isLoading,
}) => {
  if (isLoading) {
    return (
      <div style={styles.container}>
        <h2 style={styles.title}>System Prompt Compliance Analysis</h2>
        <div style={styles.loading}>Analyzing...</div>
      </div>
    );
  }

  if (!analysis) {
    return (
      <div style={styles.container}>
        <h2 style={styles.title}>System Prompt Compliance Analysis</h2>
        <div style={styles.emptyState}>
          Send a message to see compliance analysis
        </div>
      </div>
    );
  }

  const followedCount = analysis.guideline_results.filter((r) => r.followed).length;
  const notFollowedCount = analysis.guideline_results.length - followedCount;

  const chartData = [
    { name: 'Followed', value: followedCount, color: '#28a745' },
    { name: 'Not Followed', value: notFollowedCount, color: '#dc3545' },
  ];

  return (
    <div style={styles.container}>
      <h2 style={styles.title}>System Prompt Compliance Analysis</h2>

      <div style={styles.scoreSection}>
        <div style={styles.scoreCircle}>
          <div style={styles.scoreValue}>{analysis.overall_score.toFixed(1)}%</div>
          <div style={styles.scoreLabel}>Overall Compliance</div>
        </div>

        <div style={styles.chartContainer}>
          <ResponsiveContainer width="100%" height={200}>
            <PieChart>
              <Pie
                data={chartData}
                cx="50%"
                cy="50%"
                innerRadius={50}
                outerRadius={80}
                paddingAngle={5}
                dataKey="value"
              >
                {chartData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div style={styles.summarySection}>
        <h3 style={styles.sectionTitle}>Summary</h3>
        <p style={styles.summaryText}>{analysis.summary}</p>
      </div>

      <div style={styles.detailsSection}>
        <h3 style={styles.sectionTitle}>Detailed Analysis by Guideline</h3>
        {analysis.guideline_results.map((result, index) => (
          <div
            key={index}
            style={{
              ...styles.guidelineCard,
              borderLeft: `4px solid ${result.followed ? '#28a745' : '#dc3545'}`,
            }}
          >
            <div style={styles.guidelineHeader}>
              <span style={styles.guidelineStatus}>
                {result.followed ? '✓ Followed' : '✗ Not Followed'}
              </span>
              <span style={styles.guidelineNumber}>#{index + 1}</span>
            </div>
            <div style={styles.guidelineContent}>
              <div style={styles.guidelineText}>
                <strong>Guideline:</strong> {result.guideline}
              </div>
              <div style={styles.explanationText}>
                <strong>Analysis:</strong> {result.explanation}
              </div>
              {result.evidence && (
                <div style={styles.evidenceText}>
                  <strong>Evidence:</strong> "{result.evidence}"
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

const styles: Record<string, React.CSSProperties> = {
  container: {
    backgroundColor: 'white',
    borderRadius: '8px',
    boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
    padding: '20px',
  },
  title: {
    fontSize: '20px',
    fontWeight: 'bold',
    marginBottom: '20px',
    paddingBottom: '12px',
    borderBottom: '2px solid #e0e0e0',
  },
  loading: {
    textAlign: 'center',
    padding: '40px',
    color: '#666',
  },
  emptyState: {
    textAlign: 'center',
    padding: '40px',
    color: '#999',
    fontSize: '14px',
  },
  scoreSection: {
    display: 'flex',
    justifyContent: 'space-around',
    alignItems: 'center',
    marginBottom: '30px',
    padding: '20px',
    backgroundColor: '#f8f9fa',
    borderRadius: '8px',
  },
  scoreCircle: {
    textAlign: 'center',
  },
  scoreValue: {
    fontSize: '48px',
    fontWeight: 'bold',
    color: '#007bff',
  },
  scoreLabel: {
    fontSize: '14px',
    color: '#666',
    marginTop: '8px',
  },
  chartContainer: {
    width: '300px',
    height: '200px',
  },
  summarySection: {
    marginBottom: '30px',
    padding: '16px',
    backgroundColor: '#fff9e6',
    borderRadius: '6px',
    borderLeft: '4px solid #ffc107',
  },
  sectionTitle: {
    fontSize: '16px',
    fontWeight: 'bold',
    marginBottom: '12px',
  },
  summaryText: {
    fontSize: '14px',
    lineHeight: '1.6',
    color: '#333',
    margin: 0,
    whiteSpace: 'pre-wrap',
  },
  detailsSection: {
    marginTop: '20px',
  },
  guidelineCard: {
    backgroundColor: '#f9f9f9',
    padding: '16px',
    borderRadius: '6px',
    marginBottom: '12px',
  },
  guidelineHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '12px',
  },
  guidelineStatus: {
    fontSize: '14px',
    fontWeight: 'bold',
  },
  guidelineNumber: {
    fontSize: '12px',
    color: '#666',
  },
  guidelineContent: {
    fontSize: '14px',
  },
  guidelineText: {
    marginBottom: '8px',
    lineHeight: '1.5',
  },
  explanationText: {
    marginBottom: '8px',
    color: '#555',
    lineHeight: '1.5',
  },
  evidenceText: {
    padding: '8px',
    backgroundColor: '#fff',
    borderRadius: '4px',
    fontSize: '13px',
    fontStyle: 'italic',
    color: '#666',
  },
};
