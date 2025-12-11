import { useState } from "react";
import { useRouter } from "next/router";
import MobileLayout from "../components/MobileLayout";
import CameraCapture from "../components/CameraCapture";
import { uploadSelfie } from "../lib/api";
import { submitSelfie } from "../lib/orchestrate";
import { getSession } from "../lib/session";

export default function SelfiePage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSelfie(file: File) {
    const session_id = getSession();
    if (!session_id) {
      setError("Session missing. Please start over.");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      // Upload to Capture service
      const result = await uploadSelfie(file);

      // Submit to Orchestrate
      await submitSelfie(session_id, result.metadata, result.provider_result);

      router.push("/review");
    } catch (err) {
      setError("Upload failed. Please try again.");
      console.error("Selfie upload error:", err);
      setLoading(false);
    }
  }

  return (
    <MobileLayout>
      <h2 className="text-2xl font-semibold mb-2">Take a Selfie</h2>
      <p className="text-sm text-gray-600 mb-6">
        Make sure your face is clearly visible and well-lit.
      </p>

      {error && (
        <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
          {error}
        </div>
      )}

      {loading ? (
        <div className="text-center py-8">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          <p className="mt-4 text-gray-600">Uploading selfie...</p>
        </div>
      ) : (
        <CameraCapture onCapture={handleSelfie} />
      )}
    </MobileLayout>
  );
}
