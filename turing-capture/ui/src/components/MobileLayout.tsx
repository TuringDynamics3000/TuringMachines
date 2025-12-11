import React from "react";

export default function MobileLayout({ children }: { children: React.ReactNode }) {
  return (
    <div
      style={{
        maxWidth: "450px",
        margin: "0 auto",
        padding: "20px",
        fontFamily: "Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
        minHeight: "100vh",
        backgroundColor: "#f5f5f5",
      }}
    >
      <div
        style={{
          backgroundColor: "white",
          borderRadius: "12px",
          padding: "24px",
          boxShadow: "0 2px 8px rgba(0,0,0,0.1)",
        }}
      >
        {children}
      </div>
    </div>
  );
}
