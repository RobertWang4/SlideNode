import { ScrollArea } from "@/components/ui/scroll-area";
import { SectionBlock } from "@/components/editor/SectionBlock";
import type { Deck } from "@/types";
import type { DraftSection } from "@/hooks/useDeckDraft";

interface SlidePaneProps {
  deck: Deck;
  draftSections: DraftSection[];
  activeBulletId: string | null;
  onUpdateSectionHeading: (sectionId: string, heading: string) => void;
  onUpdateSubsectionHeading: (sectionId: string, subsectionId: string, heading: string) => void;
  onUpdateSubsectionAnnotation: (sectionId: string, subsectionId: string, annotation: string) => void;
  onUpdateBulletText: (sectionId: string, subsectionId: string, bulletId: string, text: string) => void;
  onBulletFocus: (bulletId: string) => void;
}

export function SlidePane({
  deck,
  draftSections,
  activeBulletId,
  onUpdateSectionHeading,
  onUpdateSubsectionHeading,
  onUpdateSubsectionAnnotation,
  onUpdateBulletText,
  onBulletFocus,
}: SlidePaneProps) {
  return (
    <ScrollArea className="h-full">
      <div className="space-y-3 p-4">
        {draftSections.map((draft, idx) => {
          const section = deck.sections[idx];
          if (!section) return null;
          return (
            <div
              key={draft.id}
              className="animate-fade-in-up"
              style={{ animationDelay: `${idx * 60}ms`, animationFillMode: "both" }}
            >
              <SectionBlock
                section={section}
                draft={draft}
                activeBulletId={activeBulletId}
                onSectionHeadingChange={(h) => onUpdateSectionHeading(draft.id, h)}
                onSubsectionHeadingChange={(subId, h) => onUpdateSubsectionHeading(draft.id, subId, h)}
                onSubsectionAnnotationChange={(subId, a) => onUpdateSubsectionAnnotation(draft.id, subId, a)}
                onBulletTextChange={(subId, bId, text) => onUpdateBulletText(draft.id, subId, bId, text)}
                onBulletFocus={onBulletFocus}
              />
            </div>
          );
        })}
      </div>
    </ScrollArea>
  );
}
