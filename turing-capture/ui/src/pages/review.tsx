import { useEffect, useState } from "react";
import { useRouter } from "next/router";
import MobileLayout from "../components/MobileLayout";
import { runRisk } from "../lib/orchestrate";
import { getSession } from "../lib/session";

export default function ReviewPage() {
  const router = useRouter();
  const [status, setStatus] = useState("Checking identity...");
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function doRisk() {
      const session_id = getSession();
      if (!session_id) {
        setError("Session missing. Please start over.");
        return;
      }

      try {
        // Simulate progress
        setProgress(20);
        setStatus("Analyzing documents...");
        
        await new Promise(resolve => setTimeout(resolve, 1000));
        setProgress(40);
        setStatus("Verifying identity...");
        
        await new Promise(resolve => setTimeout(resolve, 1000));
        setProgress(60);
        setStatus("Running risk assessment...");
        
        // Run actual risk assessment
        const risk = await runRisk(session_id);
        
        setProgress(80);
        setStatus("Finalizing...");
        
        await new Promise(resolve => setTimeout(resolve, 500));
        setProgress(100);

        // Route based on risk band
        const band = risk.risk.risk_band;

        if (band === "low") {
          router.push("/success");
        } else if (band === "medium") {
          router.push("/step-up");
        } else if (band === "high") {
          router.push("/manual-review");
        } else {
          router.push("/rejected");
        }
      } catch (err) {
        console.error("Risk assessment error:", err);
        setError("Verification failed. Please try again.");
      }
    }

    doRisk();
  }, [router]);

  return (
    <MobileLayout>
      <div className="text-center">
        <div className="mb-6">
          <div className="inline-block animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600"></div>
        </div>

        <h2 className="text-2xl font-semibold mb-4">
          Verifying your identity...
        </h2>

        <p className="text-gray-600 mb-6">{status}</p>

        {error ? (
          <div className="p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
            {error}
          </div>
        ) : (
          <div className="progress-bar">
            <div 
              className="progress-fill" 
              style={{ width: `${progress}%` }}
            ></div>
          </div>
        )}

        <p className="text-xs text-gray-400 mt-4">
          This usually takes 5-10 seconds
        </p>
      </div>
    </MobileLayout>
  );
}
