import { useCallback, useState } from "react";

import { useAppState } from "@/hooks/useAppState";
import { useJobPoller } from "@/hooks/useJobPoller";
import { useDeckDraft } from "@/hooks/useDeckDraft";
import { useCitationSync } from "@/hooks/useCitationSync";

import { AppShell } from "@/components/layout/AppShell";
import { Sidebar } from "@/components/layout/Sidebar";
import { MainContent } from "@/components/main/MainContent";
import { UploadDialog } from "@/components/upload/UploadDialog";
import { ConfirmDialog } from "@/components/shared/ConfirmDialog";

export default function App() {
  const {
    job,
    setJob,
    documents,
    activeDocumentId,
    deck,
    setDeck,
    error,
    setError,
    uploadDialogOpen,
    setUploadDialogOpen,
    handleUpload,
    openDocument,
    saveDeck,
    downloadMarkdown,
    downloadPptx,
    handleDelete,
    refreshDocuments,
  } = useAppState();

  // Job polling
  useJobPoller({
    job,
    activeDocumentId,
    onJobUpdate: setJob,
    onDeckReady: setDeck,
    onDocumentsRefresh: () => void refreshDocuments(),
    onError: setError,
  });

  // Deck draft for editing
  const {
    draftSections,
    isDirty,
    updateSectionHeading,
    updateSubsectionHeading,
    updateSubsectionAnnotation,
    updateBulletText,
    getDraftPayload,
  } = useDeckDraft(deck);

  // Citation sync
  const {
    activeBulletId,
    activeCitations,
    handleBulletFocus,
  } = useCitationSync(deck);

  // Delete confirmation dialog
  const [deleteTarget, setDeleteTarget] = useState<string | null>(null);

  const handleSave = useCallback(async () => {
    await saveDeck(getDraftPayload());
  }, [saveDeck, getDraftPayload]);

  const confirmDelete = useCallback(() => {
    if (deleteTarget) {
      void handleDelete(deleteTarget);
      setDeleteTarget(null);
    }
  }, [deleteTarget, handleDelete]);

  return (
    <>
      <AppShell
        sidebar={
          <Sidebar
            documents={documents}
            activeDocumentId={activeDocumentId}
            job={job}
            onOpenDocument={openDocument}
            onDeleteDocument={setDeleteTarget}
            onUploadClick={() => setUploadDialogOpen(true)}
          />
        }
      >
        <MainContent
          activeDocumentId={activeDocumentId}
          job={job}
          deck={deck}
          error={error}
          onDismissError={() => setError("")}
          draftSections={draftSections}
          isDirty={isDirty}
          onUpdateSectionHeading={updateSectionHeading}
          onUpdateSubsectionHeading={updateSubsectionHeading}
          onUpdateSubsectionAnnotation={updateSubsectionAnnotation}
          onUpdateBulletText={updateBulletText}
          onSave={handleSave}
          onExportMarkdown={downloadMarkdown}
          onExportPptx={downloadPptx}
          activeBulletId={activeBulletId}
          activeCitations={activeCitations}
          onBulletFocus={handleBulletFocus}
        />
      </AppShell>

      <UploadDialog
        open={uploadDialogOpen}
        onOpenChange={setUploadDialogOpen}
        onUpload={handleUpload}
      />

      <ConfirmDialog
        open={deleteTarget !== null}
        onOpenChange={(open) => {
          if (!open) setDeleteTarget(null);
        }}
        title="Delete Document"
        description="This will permanently delete this document and all its data. This action cannot be undone."
        confirmLabel="Delete"
        onConfirm={confirmDelete}
        destructive
      />
    </>
  );
}
