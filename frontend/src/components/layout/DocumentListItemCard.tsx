import { FileText, Loader2, Trash2 } from "lucide-react";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import type { DocumentListItem } from "@/types";

interface DocumentListItemCardProps {
  document: DocumentListItem;
  isActive: boolean;
  isProcessing: boolean;
  progress?: number;
  onClick: () => void;
  onDelete: () => void;
}

export function DocumentListItemCard({
  document,
  isActive,
  isProcessing,
  progress,
  onClick,
  onDelete,
}: DocumentListItemCardProps) {
  const [isHovered, setIsHovered] = useState(false);

  return (
    <div
      className={`
        group relative flex flex-col gap-1 rounded-lg px-3 py-2.5 cursor-pointer
        transition-all duration-300
        ${isActive
          ? "bg-gradient-to-r from-primary/8 to-primary/4 border border-primary/20 shadow-sm"
          : "hover:bg-card hover:shadow-sm border border-transparent hover:border-border/50"
        }
      `}
      onClick={onClick}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      <div className="flex items-start gap-2.5">
        <div
          className={`
            mt-0.5 flex h-6 w-6 shrink-0 items-center justify-center rounded-md
            transition-all duration-300
            ${isActive
              ? "gradient-primary text-white shadow-sm"
              : "bg-muted text-muted-foreground"
            }
          `}
        >
          {isProcessing ? (
            <Loader2 className="h-3.5 w-3.5 animate-spin" />
          ) : (
            <FileText className="h-3.5 w-3.5" />
          )}
        </div>

        <div className="min-w-0 flex-1">
          <p className="truncate text-sm font-medium leading-tight">
            {document.title}
          </p>
          <p className="mt-0.5 text-[11px] text-muted-foreground">
            {document.pages ? `${document.pages} pages` : document.status}
          </p>
        </div>

        {/* Delete button - shows on hover */}
        {isHovered && !isProcessing && (
          <Button
            variant="ghost"
            size="icon"
            className="h-6 w-6 shrink-0 text-muted-foreground hover:text-destructive hover:bg-destructive/10 transition-colors"
            onClick={(e) => {
              e.stopPropagation();
              onDelete();
            }}
          >
            <Trash2 className="h-3 w-3" />
          </Button>
        )}
      </div>

      {/* Progress bar for processing documents */}
      {isProcessing && progress !== undefined && (
        <div className="mt-1 pl-8">
          <Progress value={progress} className="h-1" />
          <p className="mt-0.5 text-[10px] text-muted-foreground">
            {Math.round(progress)}%
          </p>
        </div>
      )}
    </div>
  );
}
