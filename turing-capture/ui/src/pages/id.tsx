import { useState } from "react";
import { useRouter } from "next/router";
import MobileLayout from "../components/MobileLayout";
import UploadBox from "../components/UploadBox";
import { uploadID } from "../lib/api";
import { submitID } from "../lib/orchestrate";
import { getSession } from "../lib/session";

export default function IDPage() {
  const router = useRouter();
  const [front, setFront] = useState<File | null>(null);
  const [back, setBack] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function nextStep() {
    const session_id = getSession();
    if (!session_id) {
      setError("Session missing. Please start over.");
      return;
    }

    if (!front || !back) {
      setError("Please upload both sides of your ID.");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      // Upload to Capture service
      const captureResult = await uploadID(front, back);

      // Submit to Orchestrate
      await submitID(session_id, captureResult.metadata, captureResult.provider_result);

      router.push("/selfie");
    } catch (err) {
      setError("Upload failed. Please try again.");
      console.error("ID upload error:", err);
      setLoading(false);
    }
  }

  return (
    <MobileLayout>
      <h2 className="text-2xl font-semibold mb-2">Upload Your ID</h2>
      <p className="text-sm text-gray-600 mb-6">
        Please upload clear photos of both sides of your government-issued ID.
      </p>

      {error && (
        <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
          {error}
        </div>
      )}

      <UploadBox 
        label="Front of ID" 
        onSelect={setFront} 
        selected={!!front}
      />
      <UploadBox 
        label="Back of ID" 
        onSelect={setBack}
        selected={!!back}
      />

      <button 
        className="btn mt-6" 
        onClick={nextStep}
        disabled={loading || !front || !back}
      >
        {loading ? "Uploading..." : "Continue"}
      </button>
    </MobileLayout>
  );
}
