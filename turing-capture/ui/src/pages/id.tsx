import { useState } from "react";
import { useRouter } from "next/router";
import MobileLayout from "../components/MobileLayout";
import UploadBox from "../components/UploadBox";
import { uploadID } from "../lib/api";

export default function IDPage() {
  const [front, setFront] = useState<File | null>(null);
  const [back, setBack] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  async function submit() {
    if (!front || !back) {
      setError("Please upload both sides of your ID");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const res = await uploadID(front, back);
      console.log("ID result:", res);
      router.push("/selfie");
    } catch (err) {
      setError("Upload failed. Please try again.");
      console.error("Upload error:", err);
    } finally {
      setLoading(false);
    }
  }

  return (
    <MobileLayout>
      <h2 style={{ 
        fontSize: "24px", 
        marginBottom: "8px",
        color: "#333"
      }}>
        Upload Your ID
      </h2>
      <p style={{ 
        fontSize: "14px", 
        color: "#666",
        marginBottom: "16px"
      }}>
        Please upload clear photos of both sides of your government-issued ID.
      </p>

      {error && (
        <div style={{ 
          padding: "12px", 
          backgroundColor: "#fee", 
          borderRadius: "8px",
          marginBottom: "16px",
          color: "#c00"
        }}>
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
        onClick={submit}
        disabled={loading || !front || !back}
        style={{
          width: "100%",
          padding: "16px",
          backgroundColor: loading || !front || !back ? "#ccc" : "#0070f3",
          color: "white",
          border: "none",
          borderRadius: "8px",
          fontSize: "16px",
          fontWeight: "600",
          cursor: loading || !front || !back ? "not-allowed" : "pointer",
          marginTop: "24px",
        }}
      >
        {loading ? "Uploading..." : "Continue"}
      </button>
    </MobileLayout>
  );
}
