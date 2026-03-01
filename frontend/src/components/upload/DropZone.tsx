import { useCallback, useRef, useState } from "react";
import { FileUp, Upload } from "lucide-react";

interface DropZoneProps {
  onFileSelected: (file: File) => void;
  disabled?: boolean;
}

export function DropZone({ onFileSelected, disabled = false }: DropZoneProps) {
  const [isDragOver, setIsDragOver] = useState(false);
  const [fileName, setFileName] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleDragOver = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      if (!disabled) setIsDragOver(true);
    },
    [disabled]
  );

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
  }, []);

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setIsDragOver(false);
      if (disabled) return;

      const file = e.dataTransfer.files[0];
      if (file && file.type === "application/pdf") {
        setFileName(file.name);
        onFileSelected(file);
      }
    },
    [disabled, onFileSelected]
  );

  const handleFileChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0];
      if (file) {
        setFileName(file.name);
        onFileSelected(file);
      }
    },
    [onFileSelected]
  );

  return (
    <div
      className={`
        relative flex flex-col items-center justify-center gap-3 rounded-2xl border-2 border-dashed
        px-6 py-10 transition-all duration-300 cursor-pointer
        ${isDragOver
          ? "border-primary bg-primary/5 scale-[1.02] shadow-lg shadow-primary/10"
          : "border-muted-foreground/20 hover:border-primary/40 hover:bg-muted/30"
        }
        ${disabled ? "opacity-50 cursor-not-allowed" : ""}
      `}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
      onClick={() => !disabled && inputRef.current?.click()}
    >
      <div
        className={`
          flex h-12 w-12 items-center justify-center rounded-full transition-all duration-300
          ${isDragOver ? "gradient-primary text-white shadow-md scale-110" : "bg-muted text-muted-foreground"}
        `}
      >
        {fileName ? (
          <FileUp className="h-5 w-5" />
        ) : (
          <Upload className="h-5 w-5" />
        )}
      </div>

      {fileName ? (
        <div className="text-center">
          <p className="text-sm font-medium">{fileName}</p>
          <p className="mt-0.5 text-xs text-muted-foreground">Click or drop to change</p>
        </div>
      ) : (
        <div className="text-center">
          <p className="text-sm font-medium">
            Drop your PDF here, or{" "}
            <span className="font-medium text-primary underline underline-offset-2 decoration-primary/30 hover:decoration-primary/60 transition-colors">browse</span>
          </p>
          <p className="mt-0.5 text-xs text-muted-foreground">
            PDF files up to 200 pages
          </p>
        </div>
      )}

      <input
        ref={inputRef}
        type="file"
        accept="application/pdf"
        className="hidden"
        onChange={handleFileChange}
        disabled={disabled}
      />
    </div>
  );
}
