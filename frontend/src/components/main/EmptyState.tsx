import { FileText } from "lucide-react";

export function EmptyState() {
  return (
    <div className="flex h-full flex-col items-center justify-center gap-5 text-center animate-fade-in">
      <div className="gradient-primary flex h-16 w-16 items-center justify-center rounded-2xl shadow-lg">
        <FileText className="h-7 w-7 text-white" />
      </div>
      <div>
        <h2 className="text-lg font-semibold text-foreground">No document selected</h2>
        <p className="mt-1.5 max-w-[280px] text-sm text-muted-foreground leading-relaxed">
          Upload a PDF or select a document from the sidebar to get started.
        </p>
      </div>
    </div>
  );
}
