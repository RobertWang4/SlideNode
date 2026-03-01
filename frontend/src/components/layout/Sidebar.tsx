import { FileUp, Layers } from "lucide-react";

import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import { DocumentListItemCard } from "@/components/layout/DocumentListItemCard";
import type { DocumentListItem, Job } from "@/types";

interface SidebarProps {
  documents: DocumentListItem[];
  activeDocumentId: string | null;
  job: Job | null;
  onOpenDocument: (id: string) => void;
  onDeleteDocument: (id: string) => void;
  onUploadClick: () => void;
}

export function Sidebar({
  documents,
  activeDocumentId,
  job,
  onOpenDocument,
  onDeleteDocument,
  onUploadClick,
}: SidebarProps) {
  return (
    <aside className="flex w-[280px] shrink-0 flex-col border-r bg-card/80 backdrop-blur-sm">
      {/* Logo area */}
      <div className="flex items-center gap-2.5 px-5 py-5">
        <div className="gradient-primary flex h-8 w-8 items-center justify-center rounded-lg shadow-sm">
          <Layers className="h-4 w-4 text-white" />
        </div>
        <div>
          <h1 className="text-base font-semibold tracking-tight">SlideNode</h1>
          <p className="text-[11px] text-muted-foreground">PDF to learning slides</p>
        </div>
      </div>

      <div className="px-3 pb-3">
        <Button
          onClick={onUploadClick}
          className="gradient-primary w-full gap-2 border-0 shadow-sm transition-all duration-300 hover:shadow-md hover:brightness-110"
        >
          <FileUp className="h-4 w-4" />
          New Document
        </Button>
      </div>

      <Separator />

      {/* Document list */}
      <ScrollArea className="flex-1">
        <div className="p-3 space-y-1">
          {documents.length === 0 ? (
            <p className="px-2 py-8 text-center text-sm text-muted-foreground">
              No documents yet
            </p>
          ) : (
            documents.map((doc) => (
              <DocumentListItemCard
                key={doc.id}
                document={doc}
                isActive={doc.id === activeDocumentId}
                isProcessing={
                  doc.id === activeDocumentId &&
                  job !== null &&
                  (job.status === "queued" || job.status === "running")
                }
                progress={
                  doc.id === activeDocumentId && job ? job.progress : undefined
                }
                onClick={() => onOpenDocument(doc.id)}
                onDelete={() => onDeleteDocument(doc.id)}
              />
            ))
          )}
        </div>
      </ScrollArea>
    </aside>
  );
}
