import { useState } from "react";

type Props = {
  onUpload: (file: File) => Promise<void>;
};

export function UploadPanel({ onUpload }: Props) {
  const [file, setFile] = useState<File | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string>("");

  return (
    <section className="panel">
      <h2>Upload PDF</h2>
      <input
        type="file"
        accept="application/pdf"
        onChange={(e) => {
          setError("");
          setFile(e.target.files?.[0] || null);
        }}
      />
      <button
        disabled={!file || busy}
        onClick={async () => {
          if (!file) return;
          setBusy(true);
          setError("");
          try {
            await onUpload(file);
          } catch (e) {
            setError(e instanceof Error ? e.message : "Upload failed");
          } finally {
            setBusy(false);
          }
        }}
      >
        {busy ? "Uploading..." : "Start Pipeline"}
      </button>
      {error ? <p className="error">{error}</p> : null}
    </section>
  );
}
