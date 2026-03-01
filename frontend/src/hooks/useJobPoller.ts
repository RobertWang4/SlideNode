import { useEffect, useRef } from "react";

import { getDeck, getJob, listDocuments } from "@/api/client";
import type { Deck, DocumentListItem, Job } from "@/types";

interface UseJobPollerOptions {
  job: Job | null;
  activeDocumentId: string | null;
  onJobUpdate: (job: Job) => void;
  onDeckReady: (deck: Deck) => void;
  onDocumentsRefresh: (docs: DocumentListItem[]) => void;
  onError: (msg: string) => void;
}

export function useJobPoller({
  job,
  activeDocumentId,
  onJobUpdate,
  onDeckReady,
  onDocumentsRefresh,
  onError,
}: UseJobPollerOptions) {
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  useEffect(() => {
    if (!job || job.status === "done" || job.status === "failed") {
      return;
    }

    intervalRef.current = setInterval(async () => {
      try {
        const latest = await getJob(job.id);
        onJobUpdate(latest);
        if (latest.status === "done" && activeDocumentId) {
          onDeckReady(await getDeck(activeDocumentId));
          const docs = await listDocuments();
          onDocumentsRefresh(docs);
        }
      } catch (e) {
        onError(e instanceof Error ? e.message : "Polling error");
      }
    }, 5000);

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [job, activeDocumentId, onJobUpdate, onDeckReady, onDocumentsRefresh, onError]);
}
