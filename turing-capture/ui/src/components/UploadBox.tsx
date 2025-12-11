"use client";

export default function UploadBox({ 
  label, 
  onSelect,
  selected 
}: { 
  label: string; 
  onSelect: (f: File) => void;
  selected?: boolean;
}) {
  return (
    <div
      style={{
        border: selected ? "2px solid #0070f3" : "2px dashed #ccc",
        padding: "20px",
        textAlign: "center",
        borderRadius: "10px",
        marginTop: "20px",
        backgroundColor: selected ? "#f0f8ff" : "white",
        cursor: "pointer",
      }}
    >
      <p style={{ marginBottom: "12px", fontWeight: "500" }}>
        {label} {selected && "✓"}
      </p>
      <input
        type="file"
        accept="image/*"
        capture="environment"
        onChange={(e) => e.target.files && onSelect(e.target.files[0])}
        style={{
          width: "100%",
          padding: "8px",
          fontSize: "14px",
        }}
      />
    </div>
  );
}
