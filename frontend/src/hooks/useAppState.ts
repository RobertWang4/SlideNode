import { useCallback, useEffect, useState } from "react";

import {
  deleteDocument,
  exportMarkdown,
  exportPptx,
  getDeck,
  getJob,
  listDocuments,
  patchDeck,
  uploadDocument,
} from "@/api/client";
import type { Deck, DocumentListItem, Job } from "@/types";

export function useAppState() {
  const [job, setJob] = useState<Job | null>(null);
  const [documents, setDocuments] = useState<DocumentListItem[]>([]);
  const [activeDocumentId, setActiveDocumentId] = useState<string | null>(null);
  const [deck, setDeck] = useState<Deck | null>(null);
  const [error, setError] = useState("");
  const [uploadDialogOpen, setUploadDialogOpen] = useState(false);

  const refreshDocuments = useCallback(async () => {
    try {
      const items = await listDocuments();
      setDocuments(items);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load documents");
    }
  }, []);

  useEffect(() => {
    void refreshDocuments();
  }, [refreshDocuments]);

  const handleUpload = useCallback(
    async (file: File) => {
      setError("");
      try {
        const created = await uploadDocument(file);
        // Close dialog immediately — processing shows in main content
        setUploadDialogOpen(false);
        setDeck(null);
        setActiveDocumentId(created.document_id);
        const latest = await getJob(created.job_id);
        setJob(latest);
        if (latest.status === "done") {
          setDeck(await getDeck(created.document_id));
        }
        await refreshDocuments();
      } catch (e) {
        setError(e instanceof Error ? e.message : "Upload failed");
      }
    },
    [refreshDocuments]
  );

  const openDocument = useCallback(async (id: string) => {
    setError("");
    try {
      setActiveDocumentId(id);
      setDeck(await getDeck(id));
      setJob(null);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load document");
    }
  }, []);

  const saveDeck = useCallback(
    async (payload: unknown) => {
      if (!activeDocumentId) return;
      setError("");
      try {
        const updated = await patchDeck(activeDocumentId, payload);
        setDeck(updated);
      } catch (e) {
        setError(e instanceof Error ? e.message : "Save failed");
      }
    },
    [activeDocumentId]
  );

  const downloadMarkdown = useCallback(async () => {
    if (!activeDocumentId) return;
    try {
      const content = await exportMarkdown(activeDocumentId);
      const blob = new Blob([content], { type: "text/markdown" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "slidenode-export.md";
      a.click();
      URL.revokeObjectURL(url);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Export failed");
    }
  }, [activeDocumentId]);

  const downloadPptx = useCallback(async () => {
    if (!activeDocumentId) return;
    try {
      const blob = await exportPptx(activeDocumentId);
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "slidenode-export.pptx";
      a.click();
      URL.revokeObjectURL(url);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Export failed");
    }
  }, [activeDocumentId]);

  const handleDelete = useCallback(
    async (id: string) => {
      setError("");
      try {
        await deleteDocument(id);
        if (activeDocumentId === id) {
          setActiveDocumentId(null);
          setDeck(null);
          setJob(null);
        }
        await refreshDocuments();
      } catch (e) {
        setError(e instanceof Error ? e.message : "Delete failed");
      }
    },
    [activeDocumentId, refreshDocuments]
  );

  return {
    // State
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

    // Actions
    refreshDocuments,
    handleUpload,
    openDocument,
    saveDeck,
    downloadMarkdown,
    downloadPptx,
    handleDelete,
  };
}
