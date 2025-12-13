/**
 * Override Resolve Modal
 * 
 * Allows investigators to override a resolve by:
 * 1. Selecting a new outcome (approve/review/decline)
 * 2. Providing a mandatory reason
 * 3. Submitting an override.applied event
 * 
 * Design principles:
 * - Overrides never edit existing resolves
 * - Overrides always create a new resolve
 * - Override requires an explicit reason
 * - UI submits an event, not a mutation
 */

import { useState } from "react";

interface OverrideResolveModalProps {
  workflowId: string;
  onSubmit: (decision: "approve" | "review" | "decline", reason: string) => Promise<void>;
  onClose: () => void;
}

export function OverrideResolveModal({ workflowId, onSubmit, onClose }: OverrideResolveModalProps) {
  const [decision, setDecision] = useState<"approve" | "review" | "decline">("approve");
  const [reason, setReason] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit() {
    // Validate reason is provided
    if (!reason.trim()) {
      setError("Override reason is required");
      return;
    }

    setSubmitting(true);
    setError(null);

    try {
      await onSubmit(decision, reason);
      onClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to submit override");
      setSubmitting(false);
    }
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-40 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl p-6 w-96 max-w-full mx-4">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          🔁 Override Resolve
        </h3>

        <p className="text-sm text-gray-600 mb-4">
          Workflow ID: <span className="font-mono text-xs">{workflowId}</span>
        </p>

        {/* New Outcome Selection */}
        <label htmlFor="outcome" className="block mb-2 text-sm font-medium text-gray-700">
          New outcome
        </label>
        <select
          id="outcome"
          className="border border-gray-300 rounded-lg p-2 w-full mb-4 focus:ring-2 focus:ring-purple-500 focus:border-purple-500 outline-none"
          value={decision}
          onChange={(e) => setDecision(e.target.value as "approve" | "review" | "decline")}
          disabled={submitting}
        >
          <option value="approve">Approve</option>
          <option value="review">Review</option>
          <option value="decline">Decline</option>
        </select>

        {/* Reason Input */}
        <label htmlFor="reason" className="block mb-2 text-sm font-medium text-gray-700">
          Reason <span className="text-red-600">*</span>
        </label>
        <textarea
          id="reason"
          className="border border-gray-300 rounded-lg p-2 w-full mb-4 focus:ring-2 focus:ring-purple-500 focus:border-purple-500 outline-none"
          rows={3}
          value={reason}
          onChange={(e) => setReason(e.target.value)}
          placeholder="Explain why this override is necessary..."
          disabled={submitting}
        />

        {/* Error Message */}
        {error && (
          <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
            {error}
          </div>
        )}

        {/* Action Buttons */}
        <div className="flex justify-end gap-2">
          <button
            className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
            onClick={onClose}
            disabled={submitting}
          >
            Cancel
          </button>
          <button
            className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            onClick={handleSubmit}
            disabled={submitting}
          >
            {submitting ? "Submitting..." : "Override Resolve"}
          </button>
        </div>

        {/* Info Footer */}
        <p className="mt-4 text-xs text-gray-500">
          ℹ️ This will create a new resolve. The previous resolve remains in the timeline.
        </p>
      </div>
    </div>
  );
}
