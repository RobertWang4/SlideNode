import { useState } from "react";
import { ChevronDown } from "lucide-react";

import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible";
import { SubsectionBlock } from "@/components/editor/SubsectionBlock";
import type { Section } from "@/types";
import type { DraftSection } from "@/hooks/useDeckDraft";

interface SectionBlockProps {
  section: Section;
  draft: DraftSection;
  activeBulletId: string | null;
  onSectionHeadingChange: (heading: string) => void;
  onSubsectionHeadingChange: (subsectionId: string, heading: string) => void;
  onSubsectionAnnotationChange: (subsectionId: string, annotation: string) => void;
  onBulletTextChange: (subsectionId: string, bulletId: string, text: string) => void;
  onBulletFocus: (bulletId: string) => void;
}

export function SectionBlock({
  section,
  draft,
  activeBulletId,
  onSectionHeadingChange,
  onSubsectionHeadingChange,
  onSubsectionAnnotationChange,
  onBulletTextChange,
  onBulletFocus,
}: SectionBlockProps) {
  const [isOpen, setIsOpen] = useState(true);

  return (
    <Collapsible open={isOpen} onOpenChange={setIsOpen}>
      <div className="rounded-xl border bg-card shadow-sm transition-all duration-300 hover:shadow-md">
        <CollapsibleTrigger asChild>
          <div className="flex items-center gap-2.5 px-4 py-3 cursor-pointer select-none">
            <div className={`
              flex h-5 w-5 items-center justify-center rounded transition-transform duration-300
              ${isOpen ? "rotate-0" : "-rotate-90"}
            `}>
              <ChevronDown className="h-4 w-4 text-muted-foreground" />
            </div>
            <input
              type="text"
              value={draft.heading}
              onChange={(e) => onSectionHeadingChange(e.target.value)}
              onClick={(e) => e.stopPropagation()}
              className="flex-1 bg-transparent text-sm font-semibold tracking-tight outline-none"
              placeholder="Section heading"
            />
            <span className="rounded-full bg-muted px-2 py-0.5 text-[10px] font-medium text-muted-foreground shrink-0">
              {section.subsections.length} subsection{section.subsections.length !== 1 ? "s" : ""}
            </span>
          </div>
        </CollapsibleTrigger>

        <CollapsibleContent>
          <div className="space-y-4 px-4 pb-4 pt-1">
            {draft.subsections.map((draftSub, idx) => {
              const originalSub = section.subsections[idx];
              if (!originalSub) return null;
              return (
                <SubsectionBlock
                  key={draftSub.id}
                  sectionId={section.id}
                  subsection={originalSub}
                  draftHeading={draftSub.heading}
                  draftAnnotation={draftSub.annotation}
                  draftBullets={draftSub.bullets}
                  activeBulletId={activeBulletId}
                  onHeadingChange={(h) => onSubsectionHeadingChange(draftSub.id, h)}
                  onAnnotationChange={(a) => onSubsectionAnnotationChange(draftSub.id, a)}
                  onBulletTextChange={(bulletId, text) => onBulletTextChange(draftSub.id, bulletId, text)}
                  onBulletFocus={onBulletFocus}
                />
              );
            })}
          </div>
        </CollapsibleContent>
      </div>
    </Collapsible>
  );
}
