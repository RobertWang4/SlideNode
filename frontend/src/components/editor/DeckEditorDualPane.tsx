import { Separator } from "@/components/ui/separator";
import { EditorToolbar } from "@/components/editor/EditorToolbar";
import { CitationPane } from "@/components/editor/CitationPane";
import { SlidePane } from "@/components/editor/SlidePane";
import type { Deck, Citation } from "@/types";
import type { DraftSection } from "@/hooks/useDeckDraft";

interface DeckEditorDualPaneProps {
  deck: Deck;
  draftSections: DraftSection[];
  isDirty: boolean;
  onUpdateSectionHeading: (sectionId: string, heading: string) => void;
  onUpdateSubsectionHeading: (sectionId: string, subsectionId: string, heading: string) => void;
  onUpdateSubsectionAnnotation: (sectionId: string, subsectionId: string, annotation: string) => void;
  onUpdateBulletText: (sectionId: string, subsectionId: string, bulletId: string, text: string) => void;
  onSave: () => void;
  onExportMarkdown: () => void;
  onExportPptx: () => void;
  activeBulletId: string | null;
  activeCitations: Citation[];
  onBulletFocus: (bulletId: string) => void;
}

export function DeckEditorDualPane({
  deck,
  draftSections,
  isDirty,
  onUpdateSectionHeading,
  onUpdateSubsectionHeading,
  onUpdateSubsectionAnnotation,
  onUpdateBulletText,
  onSave,
  onExportMarkdown,
  onExportPptx,
  activeBulletId,
  activeCitations,
  onBulletFocus,
}: DeckEditorDualPaneProps) {
  return (
    <div className="flex h-full flex-col overflow-hidden">
      <EditorToolbar
        deck={deck}
        isDirty={isDirty}
        onSave={onSave}
        onExportMarkdown={onExportMarkdown}
        onExportPptx={onExportPptx}
      />

      <div className="flex flex-1 overflow-hidden">
        {/* Citation Pane - Left (40%) */}
        <div className="w-[40%] shrink-0 overflow-hidden border-r border-border/50 bg-muted/20">
          <CitationPane
            activeBulletId={activeBulletId}
            activeCitations={activeCitations}
          />
        </div>

        {/* Slide Pane - Right (60%) */}
        <div className="flex-1 overflow-hidden">
          <SlidePane
            deck={deck}
            draftSections={draftSections}
            activeBulletId={activeBulletId}
            onUpdateSectionHeading={onUpdateSectionHeading}
            onUpdateSubsectionHeading={onUpdateSubsectionHeading}
            onUpdateSubsectionAnnotation={onUpdateSubsectionAnnotation}
            onUpdateBulletText={onUpdateBulletText}
            onBulletFocus={onBulletFocus}
          />
        </div>
      </div>
    </div>
  );
}
