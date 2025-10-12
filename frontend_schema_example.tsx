/**
 * Frontend Integration Example for AI Summary with Schema Validation
 * 
 * This file shows how to safely consume the AI Summary API
 * with guaranteed type safety and consistent structure.
 */

// ============================================================================
// TypeScript Type Definitions
// ============================================================================

/**
 * AI Summary Response Schema
 * All fields are guaranteed to be present and of correct type
 */
interface AISummary {
  total_participants: number;
  completed_surveys: number;
  in_progress_surveys: number;
  completion_rate_percentage: number;
  positive_indicators: number;
  negative_indicators: number;
  top_keywords: string[];
  key_pain_points: string[];
  common_workflows: string[];
  technology_trends: string[];
  main_bottlenecks: string[];
  budget_insights: string;
  security_concerns: string[];
  deployment_preferences: string[];
  key_insights: string;
  recommendations: string;
}

interface SummaryResponse {
  success: boolean;
  data: {
    survey_uuid: string;
    survey_title: string;
    company: string;
    analysis_date: null;
    summary: AISummary;
    schema_validated: boolean;
    validation_errors?: string[];
    fallback?: boolean;
    error?: string;
  };
  message: string;
}

// ============================================================================
// API Client
// ============================================================================

class SurveyAPI {
  private baseUrl: string;

  constructor(baseUrl: string = 'http://localhost:8000') {
    this.baseUrl = baseUrl;
  }

  async getAISummary(surveyUuid: string): Promise<SummaryResponse> {
    const response = await fetch(`${this.baseUrl}/api/surveys/${surveyUuid}/ai-summary`);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    return await response.json();
  }
}

// ============================================================================
// React Components
// ============================================================================

import React, { useState, useEffect } from 'react';

/**
 * Main Dashboard Component
 */
export function SurveySummaryDashboard({ surveyId }: { surveyId: string }) {
  const [summary, setSummary] = useState<AISummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [validated, setValidated] = useState(true);
  const [isFallback, setIsFallback] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const api = new SurveyAPI();
    
    api.getAISummary(surveyId)
      .then(response => {
        if (response.success) {
          setSummary(response.data.summary);
          setValidated(response.data.schema_validated);
          setIsFallback(response.data.fallback || false);
          
          if (!response.data.schema_validated) {
            console.warn('Schema validation warnings:', response.data.validation_errors);
          }
        } else {
          setError('Failed to load summary');
        }
      })
      .catch(err => {
        setError(err.message);
      })
      .finally(() => {
        setLoading(false);
      });
  }, [surveyId]);

  if (loading) return <LoadingSpinner />;
  if (error) return <ErrorMessage message={error} />;
  if (!summary) return <NoDataMessage />;

  return (
    <div className="survey-dashboard">
      {/* Warning Banner for Validation Issues */}
      {!validated && (
        <WarningBanner 
          message="Some analysis data may be incomplete or estimated" 
        />
      )}
      
      {/* Fallback Notice */}
      {isFallback && (
        <InfoBanner 
          message="Using default analysis. More survey responses needed for detailed insights." 
        />
      )}

      {/* Metrics Grid */}
      <MetricsGrid summary={summary} />

      {/* Keywords Cloud */}
      <KeywordSection keywords={summary.top_keywords} />

      {/* Pain Points */}
      <PainPointsSection painPoints={summary.key_pain_points} />

      {/* Workflows & Trends */}
      <WorkflowsSection workflows={summary.common_workflows} />
      <TrendsSection trends={summary.technology_trends} />

      {/* Insights & Recommendations */}
      <InsightsPanel 
        insights={summary.key_insights}
        recommendations={summary.recommendations}
      />

      {/* Detailed Sections */}
      <BottlenecksSection bottlenecks={summary.main_bottlenecks} />
      <BudgetSection insights={summary.budget_insights} />
      <SecuritySection concerns={summary.security_concerns} />
      <DeploymentSection preferences={summary.deployment_preferences} />
    </div>
  );
}

/**
 * Metrics Grid Component
 * Safe to access all numeric fields - guaranteed to exist
 */
function MetricsGrid({ summary }: { summary: AISummary }) {
  const metrics = [
    {
      label: 'Total Participants',
      value: summary.total_participants,
      icon: '👥'
    },
    {
      label: 'Completed',
      value: summary.completed_surveys,
      icon: '✅'
    },
    {
      label: 'In Progress',
      value: summary.in_progress_surveys,
      icon: '⏳'
    },
    {
      label: 'Completion Rate',
      value: `${summary.completion_rate_percentage.toFixed(1)}%`,
      icon: '📊'
    },
    {
      label: 'Positive Indicators',
      value: summary.positive_indicators,
      icon: '😊',
      color: 'green'
    },
    {
      label: 'Negative Indicators',
      value: summary.negative_indicators,
      icon: '⚠️',
      color: 'red'
    }
  ];

  return (
    <div className="metrics-grid">
      {metrics.map((metric, i) => (
        <MetricCard key={i} {...metric} />
      ))}
    </div>
  );
}

/**
 * Keyword Cloud Component
 * Safe to iterate - always an array (may be empty)
 */
function KeywordSection({ keywords }: { keywords: string[] }) {
  if (keywords.length === 0) {
    return <EmptyState message="No keywords identified yet" />;
  }

  return (
    <section className="keywords-section">
      <h2>🔑 Top Keywords</h2>
      <div className="keyword-cloud">
        {keywords.map((keyword, i) => (
          <span 
            key={i} 
            className="keyword-tag"
            style={{ 
              fontSize: `${Math.max(14, 20 - i * 2)}px`,
              opacity: Math.max(0.5, 1 - i * 0.1)
            }}
          >
            {keyword}
          </span>
        ))}
      </div>
    </section>
  );
}

/**
 * Pain Points Component
 * Safe to iterate and rank
 */
function PainPointsSection({ painPoints }: { painPoints: string[] }) {
  if (painPoints.length === 0) {
    return <EmptyState message="No pain points identified yet" />;
  }

  return (
    <section className="pain-points-section">
      <h2>⚠️ Key Pain Points</h2>
      <ol className="pain-points-list">
        {painPoints.map((point, i) => (
          <li key={i} className="pain-point-item">
            <span className="rank">#{i + 1}</span>
            <span className="text">{point}</span>
          </li>
        ))}
      </ol>
    </section>
  );
}

/**
 * Insights Panel Component
 * Safe to render strings - always present
 */
function InsightsPanel({ 
  insights, 
  recommendations 
}: { 
  insights: string; 
  recommendations: string; 
}) {
  return (
    <section className="insights-panel">
      <div className="insight-card">
        <h3>💡 Key Insights</h3>
        <p className="insight-text">{insights}</p>
      </div>
      
      <div className="recommendations-card">
        <h3>✅ Recommendations</h3>
        <p className="recommendation-text">{recommendations}</p>
      </div>
    </section>
  );
}

/**
 * Workflows Section
 */
function WorkflowsSection({ workflows }: { workflows: string[] }) {
  if (workflows.length === 0) return null;

  return (
    <section className="workflows-section">
      <h2>🔄 Common Workflows</h2>
      <ul className="workflows-list">
        {workflows.map((workflow, i) => (
          <li key={i}>{workflow}</li>
        ))}
      </ul>
    </section>
  );
}

/**
 * Technology Trends Section
 */
function TrendsSection({ trends }: { trends: string[] }) {
  if (trends.length === 0) return null;

  return (
    <section className="trends-section">
      <h2>🚀 Technology Trends</h2>
      <div className="trends-grid">
        {trends.map((trend, i) => (
          <div key={i} className="trend-card">
            {trend}
          </div>
        ))}
      </div>
    </section>
  );
}

// ============================================================================
// Utility Components
// ============================================================================

function MetricCard({ 
  label, 
  value, 
  icon, 
  color 
}: { 
  label: string; 
  value: string | number; 
  icon: string; 
  color?: string;
}) {
  return (
    <div className={`metric-card ${color || ''}`}>
      <div className="metric-icon">{icon}</div>
      <div className="metric-value">{value}</div>
      <div className="metric-label">{label}</div>
    </div>
  );
}

function WarningBanner({ message }: { message: string }) {
  return (
    <div className="banner warning">
      ⚠️ {message}
    </div>
  );
}

function InfoBanner({ message }: { message: string }) {
  return (
    <div className="banner info">
      ℹ️ {message}
    </div>
  );
}

function LoadingSpinner() {
  return <div className="spinner">Loading summary...</div>;
}

function ErrorMessage({ message }: { message: string }) {
  return <div className="error">Error: {message}</div>;
}

function NoDataMessage() {
  return <div className="no-data">No summary data available</div>;
}

function EmptyState({ message }: { message: string }) {
  return <div className="empty-state">{message}</div>;
}

function BottlenecksSection({ bottlenecks }: { bottlenecks: string[] }) {
  if (bottlenecks.length === 0) return null;
  return (
    <section>
      <h2>🛑 Main Bottlenecks</h2>
      <ul>{bottlenecks.map((b, i) => <li key={i}>{b}</li>)}</ul>
    </section>
  );
}

function BudgetSection({ insights }: { insights: string }) {
  return (
    <section>
      <h2>💰 Budget Insights</h2>
      <p>{insights}</p>
    </section>
  );
}

function SecuritySection({ concerns }: { concerns: string[] }) {
  if (concerns.length === 0) return null;
  return (
    <section>
      <h2>🔒 Security Concerns</h2>
      <ul>{concerns.map((c, i) => <li key={i}>{c}</li>)}</ul>
    </section>
  );
}

function DeploymentSection({ preferences }: { preferences: string[] }) {
  if (preferences.length === 0) return null;
  return (
    <section>
      <h2>☁️ Deployment Preferences</h2>
      <ul>{preferences.map((p, i) => <li key={i}>{p}</li>)}</ul>
    </section>
  );
}

// ============================================================================
// Export for use in your app
// ============================================================================

export default SurveySummaryDashboard;
export type { AISummary, SummaryResponse };
export { SurveyAPI };

