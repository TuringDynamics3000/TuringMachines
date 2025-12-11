import Link from "next/link";
import MobileLayout from "../components/MobileLayout";

export default function Home() {
  return (
    <MobileLayout>
      <div style={{ textAlign: "center" }}>
        <h1 style={{ 
          fontSize: "28px", 
          marginBottom: "16px",
          color: "#333"
        }}>
          TuringCapture™
        </h1>
        <p style={{ 
          fontSize: "16px", 
          color: "#666",
          marginBottom: "32px",
          lineHeight: "1.6"
        }}>
          Identity Verification
        </p>
        <p style={{ 
          fontSize: "14px", 
          color: "#888",
          marginBottom: "32px"
        }}>
          Please follow the steps to verify your identity securely.
        </p>
        <Link href="/id">
          <button
            style={{
              width: "100%",
              padding: "16px",
              backgroundColor: "#0070f3",
              color: "white",
              border: "none",
              borderRadius: "8px",
              fontSize: "16px",
              fontWeight: "600",
              cursor: "pointer",
            }}
          >
            Start ID Capture
          </button>
        </Link>
      </div>
    </MobileLayout>
  );
}
