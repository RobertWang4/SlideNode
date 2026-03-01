import { Download, FileDown, Save } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { QualityBadge } from "@/components/shared/QualityBadge";
import type { Deck } from "@/types";

interface EditorToolbarProps {
  deck: Deck;
  isDirty: boolean;
  onSave: () => void;
  onExportMarkdown: () => void;
  onExportPptx: () => void;
}

export function EditorToolbar({
  deck,
  isDirty,
  onSave,
  onExportMarkdown,
  onExportPptx,
}: EditorToolbarProps) {
  return (
    <div className="relative flex shrink-0 items-center justify-between border-b px-5 py-3 bg-card/50 backdrop-blur-sm">
      <div className="flex items-center gap-3 min-w-0">
        <h2 className="truncate text-base font-semibold">{deck.title}</h2>
        <div className="flex shrink-0 items-center gap-1.5">
          <QualityBadge label="Coverage" value={deck.quality_report.coverage_ratio} />
          <QualityBadge label="Citations" value={deck.quality_report.citation_completeness} threshold={1.0} />
        </div>
      </div>

      <div className="flex items-center gap-2">
        <Button
          variant={isDirty ? "default" : "outline"}
          size="sm"
          onClick={onSave}
          disabled={!isDirty}
          className={`
            gap-1.5 transition-all duration-300
            ${isDirty ? "gradient-primary border-0 shadow-sm hover:shadow-md hover:brightness-110" : ""}
          `}
        >
          <Save className="h-3.5 w-3.5" />
          Save
        </Button>
        <Separator orientation="vertical" className="h-5" />
        <Button
          variant="ghost"
          size="sm"
          onClick={onExportMarkdown}
          className="gap-1.5"
        >
          <Download className="h-3.5 w-3.5" />
          MD
        </Button>
        <Button
          variant="ghost"
          size="sm"
          onClick={onExportPptx}
          className="gap-1.5"
        >
          <FileDown className="h-3.5 w-3.5" />
          PPTX
        </Button>
      </div>
    </div>
  );
}
