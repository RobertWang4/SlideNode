import { useEffect, useRef } from "react";
import { BookOpen } from "lucide-react";

import { ScrollArea } from "@/components/ui/scroll-area";
import { CitationCard } from "@/components/editor/CitationCard";
import type { Citation } from "@/types";

interface CitationPaneProps {
  activeBulletId: string | null;
  activeCitations: Citation[];
}

export function CitationPane({ activeBulletId, activeCitations }: CitationPaneProps) {
  const containerRef = useRef<HTMLDivElement>(null);

  // Scroll to top when active bullet changes
  useEffect(() => {
    if (containerRef.current && activeBulletId) {
      containerRef.current.scrollTo({ top: 0, behavior: "smooth" });
    }
  }, [activeBulletId]);

  if (!activeBulletId) {
    return (
      <div className="flex h-full flex-col items-center justify-center gap-3 text-center px-6">
        <div className="gradient-primary flex h-12 w-12 items-center justify-center rounded-xl shadow-sm">
          <BookOpen className="h-5 w-5 text-white" />
        </div>
        <div>
          <p className="text-sm font-medium text-foreground">Source Citations</p>
          <p className="mt-0.5 text-xs text-muted-foreground">
            Click a bullet point to see its citations here
          </p>
        </div>
      </div>
    );
  }

  if (activeCitations.length === 0) {
    return (
      <div className="flex h-full flex-col items-center justify-center gap-2 px-6">
        <p className="text-sm text-muted-foreground">No citations for this bullet</p>
      </div>
    );
  }

  return (
    <ScrollArea className="h-full" ref={containerRef}>
      <div className="space-y-2 p-4">
        <p className="text-[11px] font-semibold uppercase tracking-widest text-muted-foreground/70 mb-3">
          {activeCitations.length} citation{activeCitations.length !== 1 ? "s" : ""}
        </p>
        {activeCitations.map((c, i) => (
          <div
            key={`${c.page}-${c.paragraph_index}-${i}`}
            className="animate-fade-in-up"
            style={{ animationDelay: `${i * 50}ms`, animationFillMode: "both" }}
          >
            <CitationCard citation={c} isActive={true} />
          </div>
        ))}
      </div>
    </ScrollArea>
  );
}
