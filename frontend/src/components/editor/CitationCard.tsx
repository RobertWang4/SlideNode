import { Badge } from "@/components/ui/badge";
import type { Citation } from "@/types";

interface CitationCardProps {
  citation: Citation;
  isActive: boolean;
}

export function CitationCard({ citation, isActive }: CitationCardProps) {
  return (
    <div
      data-citation-page={citation.page}
      className={`
        rounded-xl border p-3.5 transition-all duration-300
        ${isActive
          ? "bg-card border-primary/20 shadow-sm"
          : "border-transparent bg-muted/30 hover:bg-muted/50"
        }
      `}
    >
      <div className="flex items-start gap-2.5">
        <Badge
          className={`
            shrink-0 text-[10px] font-mono border-0 transition-colors
            ${isActive ? "gradient-primary text-white shadow-sm" : "bg-muted text-muted-foreground"}
          `}
        >
          p.{citation.page}
        </Badge>
        <p className="text-[13px] leading-relaxed text-foreground/75">
          {citation.quote_snippet}
        </p>
      </div>
    </div>
  );
}
