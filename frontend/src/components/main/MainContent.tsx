import { EmptyState } from "@/components/main/EmptyState";
import { ProcessingState } from "@/components/main/ProcessingState";
import { DeckEditorDualPane } from "@/components/editor/DeckEditorDualPane";
import { ErrorAlert } from "@/components/shared/ErrorAlert";
import type { Deck, Job } from "@/types";
import type { DraftSection } from "@/hooks/useDeckDraft";
import type { Citation } from "@/types";

interface MainContentProps {
  activeDocumentId: string | null;
  job: Job | null;
  deck: Deck | null;
  error: string;
  onDismissError: () => void;

  // Deck draft props
  draftSections: DraftSection[];
  isDirty: boolean;
  onUpdateSectionHeading: (sectionId: string, heading: string) => void;
  onUpdateSubsectionHeading: (sectionId: string, subsectionId: string, heading: string) => void;
  onUpdateSubsectionAnnotation: (sectionId: string, subsectionId: string, annotation: string) => void;
  onUpdateBulletText: (sectionId: string, subsectionId: string, bulletId: string, text: string) => void;
  onSave: () => void;
  onExportMarkdown: () => void;
  onExportPptx: () => void;

  // Citation sync
  activeBulletId: string | null;
  activeCitations: Citation[];
  onBulletFocus: (bulletId: string) => void;
}

export function MainContent({
  activeDocumentId,
  job,
  deck,
  error,
  onDismissError,
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
}: MainContentProps) {
  // No document selected
  if (!activeDocumentId) {
    return (
      <div className="flex h-full flex-col">
        {error && (
          <div className="p-4">
            <ErrorAlert message={error} onDismiss={onDismissError} />
          </div>
        )}
        <EmptyState />
      </div>
    );
  }

  // Processing state
  const isProcessing =
    job && (job.status === "queued" || job.status === "running" || job.status === "failed") && !deck;

  if (isProcessing) {
    return <ProcessingState job={job} error={error} onDismissError={onDismissError} />;
  }

  // Deck loaded
  if (deck) {
    return (
      <div className="flex h-full flex-col overflow-hidden">
        {error && (
          <div className="shrink-0 p-4 pb-0">
            <ErrorAlert message={error} onDismiss={onDismissError} />
          </div>
        )}
        <DeckEditorDualPane
          deck={deck}
          draftSections={draftSections}
          isDirty={isDirty}
          onUpdateSectionHeading={onUpdateSectionHeading}
          onUpdateSubsectionHeading={onUpdateSubsectionHeading}
          onUpdateSubsectionAnnotation={onUpdateSubsectionAnnotation}
          onUpdateBulletText={onUpdateBulletText}
          onSave={onSave}
          onExportMarkdown={onExportMarkdown}
          onExportPptx={onExportPptx}
          activeBulletId={activeBulletId}
          activeCitations={activeCitations}
          onBulletFocus={onBulletFocus}
        />
      </div>
    );
  }

  // Fallback: loading
  return <EmptyState />;
}
