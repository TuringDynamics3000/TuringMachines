"use client";

import { useRef, useState } from "react";

export default function CameraCapture({ onCapture }: { onCapture: (f: File) => void }) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const [started, setStarted] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const startCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ 
        video: { facingMode: "user" } 
      });
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        setStarted(true);
        setError(null);
      }
    } catch (err) {
      setError("Camera access denied. Please enable camera permissions.");
      console.error("Camera error:", err);
    }
  };

  const capture = () => {
    const canvas = document.createElement("canvas");
    const video = videoRef.current!;
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    canvas.getContext("2d")!.drawImage(video, 0, 0);

    canvas.toBlob((blob) => {
      if (!blob) return;
      const file = new File([blob], "selfie.jpg", { type: "image/jpeg" });
      
      // Stop camera stream
      const stream = video.srcObject as MediaStream;
      stream?.getTracks().forEach(track => track.stop());
      
      onCapture(file);
    }, "image/jpeg");
  };

  return (
    <div style={{ marginTop: "20px" }}>
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
      
      {!started && (
        <button 
          onClick={startCamera} 
          className="btn"
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
          Start Camera
        </button>
      )}

      {started && (
        <>
          <video 
            ref={videoRef} 
            autoPlay 
            playsInline 
            style={{ 
              width: "100%", 
              borderRadius: "10px",
              marginBottom: "16px"
            }} 
          />
          <button 
            onClick={capture} 
            className="btn"
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
            Capture Selfie
          </button>
        </>
      )}
    </div>
  );
}
