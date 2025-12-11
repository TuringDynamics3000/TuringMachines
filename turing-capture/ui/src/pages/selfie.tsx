import { useState } from "react";
import { useRouter } from "next/router";
import MobileLayout from "../components/MobileLayout";
import CameraCapture from "../components/CameraCapture";
import { uploadSelfie } from "../lib/api";

export default function SelfiePage() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  async function handleSelfie(file: File) {
    setLoading(true);
    setError(null);

    try {
      const res = await uploadSelfie(file);
      console.log("Selfie result:", res);
      router.push("/review");
    } catch (err) {
      setError("Upload failed. Please try again.");
      console.error("Upload error:", err);
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
        Take a Selfie
      </h2>
      <p style={{ 
        fontSize: "14px", 
        color: "#666",
        marginBottom: "16px"
      }}>
        Position your face in the center and ensure good lighting.
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

      {loading && (
        <div style={{ 
          padding: "16px", 
          textAlign: "center",
          color: "#666"
        }}>
          Uploading selfie...
        </div>
      )}

      {!loading && <CameraCapture onCapture={handleSelfie} />}
    </MobileLayout>
  );
}
