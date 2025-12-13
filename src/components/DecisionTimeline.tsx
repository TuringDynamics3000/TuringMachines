import { useState, useEffect } from 'react';

interface Decision {
  decision_id: string;
  timestamp: string;
  outcome: string;
  confidence: number;
  requires_human: boolean;
  can_proceed: boolean;
  policy: {
    jurisdiction: string;
    policy_pack: string;
    policy_version: string;
  };
  reason_codes: string[];
  risk_summary: {
    overall_risk: string;
    risk_score: number;
  };
  authority: {
    decided_by: string;
    service_version: string;
    is_override: boolean;
  };
  lineage: {
    supersedes_decision_id?: string;
    overridden_by?: string;
    override_reason?: string;
  } | null;
  subject: {
    subject_type: string;
    subject_id: string;
    action: string;
  };
}

interface DecisionTimelineResponse {
  workflow_id: string;
  decision_count: number;
  current_decision: Decision;
  timeline: Decision[];
  has_overrides: boolean;
}

interface DecisionTimelineProps {
  workflowId: string;
  apiBaseUrl?: string;
}

export default function DecisionTimeline({ 
  workflowId, 
  apiBaseUrl = 'http://127.0.0.1:8100' 
}: DecisionTimelineProps ) {
  const [data, setData] = useState<DecisionTimelineResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchDecisions = async () => {
      try {
        setLoading(true);
        const response = await fetch(
          `${apiBaseUrl}/v1/investigator/workflows/${workflowId}/decisions`
        );
        
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const result = await response.json();
        setData(result);
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch decisions');
      } finally {
        setLoading(false);
      }
    };

    if (workflowId) {
      fetchDecisions();
    }
  }, [workflowId, apiBaseUrl]);

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <h3 className="text-red-800 font-semibold">Error Loading Decisions</h3>
        <p className="text-red-600 text-sm mt-1">{error}</p>
      </div>
    );
  }

  if (!data) {
    return null;
  }

  const getOutcomeColor = (outcome: string) => {
    switch (outcome) {
      case 'approve': return 'bg-green-100 text-green-800 border-green-300';
      case 'decline': return 'bg-red-100 text-red-800 border-red-300';
      case 'review': return 'bg-yellow-100 text-yellow-800 border-yellow-300';
      default: return 'bg-gray-100 text-gray-800 border-gray-300';
    }
  };

  const getRiskColor = (risk: string) => {
    switch (risk?.toLowerCase()) {
      case 'low': return 'text-green-600';
      case 'medium': return 'text-yellow-600';
      case 'high': return 'text-red-600';
      default: return 'text-gray-600';
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-6">
      {/* Header */}
      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        <h1 className="text-2xl font-bold text-gray-900 mb-2">
          Decision Timeline
        </h1>
        <p className="text-gray-600">Workflow ID: <span className="font-mono text-sm">{data.workflow_id}</span></p>
        
        <div className="mt-4 flex gap-4">
          <div className="bg-blue-50 px-4 py-2 rounded-lg">
            <span className="text-blue-600 font-semibold">{data.decision_count}</span>
            <span className="text-blue-800 ml-2">Decision{data.decision_count !== 1 ? 's' : ''}</span>
          </div>
          
          {data.has_overrides && (
            <div className="bg-orange-50 px-4 py-2 rounded-lg">
              <span className="text-orange-600 font-semibold">⚠️</span>
              <span className="text-orange-800 ml-2">Has Overrides</span>
            </div>
          )}
        </div>
      </div>

      {/* Current Decision */}
      <div className="bg-gradient-to-r from-blue-50 to-blue-100 rounded-lg shadow-md p-6 mb-6 border-2 border-blue-300">
        <h2 className="text-lg font-semibold text-blue-900 mb-4">🔒 Current Decision</h2>
        
        <div className="grid grid-cols-2 gap-4">
          <div>
            <p className="text-sm text-blue-700 font-medium">Outcome</p>
            <span className={`inline-block px-3 py-1 rounded-full text-sm font-semibold border mt-1 ${getOutcomeColor(data.current_decision.outcome)}`}>
              {data.current_decision.outcome.toUpperCase()}
            </span>
          </div>
          
          <div>
            <p className="text-sm text-blue-700 font-medium">Confidence</p>
            <p className="text-lg font-semibold text-blue-900">
              {(data.current_decision.confidence * 100).toFixed(0)}%
            </p>
          </div>
          
          <div>
            <p className="text-sm text-blue-700 font-medium">Risk Level</p>
            <p className={`text-lg font-semibold ${getRiskColor(data.current_decision.risk_summary.overall_risk)}`}>
              {data.current_decision.risk_summary.overall_risk?.toUpperCase() || 'N/A'}
            </p>
          </div>
          
          <div>
            <p className="text-sm text-blue-700 font-medium">Authority</p>
            <p className="text-sm font-mono text-blue-900">
              {data.current_decision.authority.decided_by}
            </p>
          </div>
        </div>
      </div>

      {/* Timeline */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">📅 Decision History</h2>
        
        <div className="space-y-4">
          {data.timeline.map((decision, index) => (
            <div 
              key={decision.decision_id}
              className={`border-l-4 pl-4 py-3 ${
                index === data.timeline.length - 1 
                  ? 'border-blue-500 bg-blue-50' 
                  : 'border-gray-300 bg-gray-50'
              } rounded-r-lg`}
            >
              <div className="flex justify-between items-start mb-2">
                <div>
                  <span className={`inline-block px-2 py-1 rounded text-xs font-semibold border ${getOutcomeColor(decision.outcome)}`}>
                    {decision.outcome.toUpperCase()}
                  </span>
                  
                  {decision.authority.is_override && (
                    <span className="ml-2 inline-block px-2 py-1 rounded text-xs font-semibold bg-orange-100 text-orange-800 border border-orange-300">
                      🔄 OVERRIDE
                    </span>
                  )}
                </div>
                
                <span className="text-xs text-gray-500">
                  {new Date(decision.timestamp).toLocaleString()}
                </span>
              </div>
              
              <div className="text-sm text-gray-700 space-y-1">
                <p><strong>Decision ID:</strong> <span className="font-mono text-xs">{decision.decision_id}</span></p>
                <p><strong>Confidence:</strong> {(decision.confidence * 100).toFixed(0)}%</p>
                <p><strong>Decided by:</strong> {decision.authority.decided_by}</p>
                
                {decision.lineage?.supersedes_decision_id && (
                  <p className="text-orange-700">
                    <strong>Supersedes:</strong> <span className="font-mono text-xs">{decision.lineage.supersedes_decision_id}</span>
                  </p>
                )}
                
                {decision.reason_codes.length > 0 && (
                  <p><strong>Reasons:</strong> {decision.reason_codes.join(', ')}</p>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
