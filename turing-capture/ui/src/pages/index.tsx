import { useState } from "react";
import { useRouter } from "next/router";
import MobileLayout from "../components/MobileLayout";
import { startSession } from "../lib/orchestrate";
import { setSession } from "../lib/session";

export default function Home() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function begin() {
    setLoading(true);
    setError(null);

    try {
      const res = await startSession("cu-001");
      setSession(res.session_id);
      router.push("/id");
    } catch (err) {
      setError("Failed to start session. Please try again.");
      console.error("Session start error:", err);
      setLoading(false);
    }
  }

  return (
    <MobileLayout>
      <div className="text-center">
        <h1 className="text-3xl font-bold mb-4 text-gray-900">
          TuringIdentity™
        </h1>
        <p className="text-lg text-gray-600 mb-2">
          Verify Your Identity
        </p>
        <p className="text-sm text-gray-500 mb-8">
          This process takes about 60 seconds.
        </p>

        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
            {error}
          </div>
        )}

        <button 
          className="btn" 
          onClick={begin}
          disabled={loading}
        >
          {loading ? "Starting..." : "Start ID Capture"}
        </button>

        <div className="mt-8 text-xs text-gray-400">
          <p>✓ Bank-grade security</p>
          <p>✓ AI-powered verification</p>
          <p>✓ Privacy protected</p>
        </div>
      </div>
    </MobileLayout>
  );
}
