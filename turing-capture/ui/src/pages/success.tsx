import MobileLayout from "../components/MobileLayout";

export default function SuccessPage() {
  return (
    <MobileLayout>
      <div style={{ textAlign: "center" }}>
        <div style={{
          fontSize: "64px",
          marginBottom: "24px"
        }}>
          ✓
        </div>
        <h2 style={{ 
          fontSize: "28px", 
          marginBottom: "16px",
          color: "#0c6",
          fontWeight: "700"
        }}>
          Identity Verified
        </h2>
        <p style={{ 
          fontSize: "16px", 
          color: "#666",
          marginBottom: "32px",
          lineHeight: "1.6"
        }}>
          Thank you for completing the verification process.
          You may now continue with your application.
        </p>

        <div style={{
          padding: "16px",
          backgroundColor: "#f0fff4",
          borderRadius: "8px",
          border: "1px solid #0c6",
          marginTop: "24px"
        }}>
          <p style={{ 
            fontSize: "14px", 
            color: "#0c6",
            fontWeight: "600",
            margin: 0
          }}>
            Verification Complete
          </p>
          <p style={{ 
            fontSize: "12px", 
            color: "#666",
            margin: "8px 0 0 0"
          }}>
            Your identity has been successfully verified and recorded.
          </p>
        </div>
      </div>
    </MobileLayout>
  );
}
