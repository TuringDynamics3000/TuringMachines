import { useEffect, useState } from "react";
import { useRouter } from "next/router";
import MobileLayout from "../components/MobileLayout";

export default function ReviewPage() {
  const [progress, setProgress] = useState(0);
  const router = useRouter();

  useEffect(() => {
    // Simulate review progress
    const interval = setInterval(() => {
      setProgress((prev) => {
        if (prev >= 100) {
          clearInterval(interval);
          // Auto-advance to success after review
          setTimeout(() => router.push("/success"), 500);
          return 100;
        }
        return prev + 10;
      });
    }, 500);

    return () => clearInterval(interval);
  }, [router]);

  return (
    <MobileLayout>
      <div style={{ textAlign: "center" }}>
        <h2 style={{ 
          fontSize: "24px", 
          marginBottom: "16px",
          color: "#333"
        }}>
          Reviewing Your Identity
        </h2>
        <p style={{ 
          fontSize: "14px", 
          color: "#666",
          marginBottom: "32px"
        }}>
          This normally takes 5–10 seconds.
        </p>

        {/* Progress Bar */}
        <div style={{
          width: "100%",
          height: "8px",
          backgroundColor: "#e0e0e0",
          borderRadius: "4px",
          overflow: "hidden",
          marginBottom: "16px"
        }}>
          <div style={{
            width: `${progress}%`,
            height: "100%",
            backgroundColor: "#0070f3",
            transition: "width 0.5s ease"
          }} />
        </div>

        <p style={{ 
          fontSize: "16px", 
          color: "#0070f3",
          fontWeight: "600"
        }}>
          {progress}%
        </p>

        <div style={{ 
          marginTop: "32px",
          fontSize: "14px",
          color: "#888"
        }}>
          <p>✓ Document verification</p>
          <p>✓ Selfie analysis</p>
          <p>✓ Risk assessment</p>
        </div>
      </div>
    </MobileLayout>
  );
}
