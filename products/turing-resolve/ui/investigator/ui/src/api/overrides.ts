/**
 * Override API Client
 * 
 * Submits override.applied events to the orchestrator.
 * The backend authority will emit the authoritative decision.finalised event.
 * 
 * This client does NOT create resolves directly - it only submits override requests.
 */

export interface OverrideParams {
  workflowId: string;
  newDecision: "approve" | "review" | "decline";
  reason: string;
  authorizedBy: string;
}

export async function submitOverride(params: OverrideParams): Promise<void> {
  const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8100";
  
  const res = await fetch(`${apiBaseUrl}/v1/orchestrate/event`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      event_type: "override.applied",
      payload: {
        workflow_id: params.workflowId,
        tenant_id: "default", // TODO: inject from auth context
        new_decision: params.newDecision,
        reason: params.reason,
        authorized_by: params.authorizedBy,
      },
      correlation_id: `override-${params.workflowId}-${Date.now()}`,
    }),
  });

  if (!res.ok) {
    const errorText = await res.text().catch(() => "Unknown error");
    throw new Error(`Failed to submit override: ${res.status} ${errorText}`);
  }
}
