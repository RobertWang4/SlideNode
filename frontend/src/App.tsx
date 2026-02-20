import { useEffect, useState } from "react";

import { deleteDocument, exportMarkdown, exportPptx, getDeck, getJob, listDocuments, patchDeck, uploadDocument } from "./api/client";
import { DeckEditor } from "./components/DeckEditor";
import { JobStatusPanel } from "./components/JobStatusPanel";
import { UploadPanel } from "./components/UploadPanel";
import type { Deck, DocumentListItem, Job } from "./types";

export default function App() {
  const [job, setJob] = useState<Job | null>(null);
  const [documents, setDocuments] = useState<DocumentListItem[]>([]);
  const [activeDocumentId, setActiveDocumentId] = useState<string | null>(null);
  const [deck, setDeck] = useState<Deck | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    void refreshDocuments();
  }, []);

  useEffect(() => {
    if (!job || job.status === "done" || job.status === "failed") return;
    const timer = setInterval(async () => {
      try {
        const latest = await getJob(job.id);
        setJob(latest);
        if (latest.status === "done" && activeDocumentId) {
          setDeck(await getDeck(activeDocumentId));
          await refreshDocuments();
        }
      } catch (e) {
        setError(e instanceof Error ? e.message : "Polling error");
      }
    }, 5000);
    return () => clearInterval(timer);
  }, [job, activeDocumentId]);

  async function refreshDocuments() {
    const items = await listDocuments();
    setDocuments(items);
  }

  async function handleUpload(file: File) {
    setError("");
    const created = await uploadDocument(file);
    setActiveDocumentId(created.document_id);
    const latest = await getJob(created.job_id);
    setJob(latest);
    if (latest.status === "done") {
      setDeck(await getDeck(created.document_id));
      await refreshDocuments();
    }
  }

  async function openDocument(id: string) {
    setActiveDocumentId(id);
    setDeck(await getDeck(id));
  }

  async function saveDeck(payload: unknown) {
    if (!activeDocumentId) return;
    const updated = await patchDeck(activeDocumentId, payload);
    setDeck(updated);
  }

  async function downloadMarkdown() {
    if (!activeDocumentId) return;
    const content = await exportMarkdown(activeDocumentId);
    const blob = new Blob([content], { type: "text/markdown" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "slidenode-export.md";
    a.click();
    URL.revokeObjectURL(url);
  }

  async function downloadPptx() {
    if (!activeDocumentId) return;
    const blob = await exportPptx(activeDocumentId);
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "slidenode-export.pptx";
    a.click();
    URL.revokeObjectURL(url);
  }

  async function handleDelete(id: string) {
    if (!confirm("Delete this document and all its data?")) return;
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
  }

  return (
    <main className="layout">
      <header>
        <h1>SlideNode</h1>
        <p>PDF → structured learning slides</p>
      </header>

      <UploadPanel onUpload={handleUpload} />
      <JobStatusPanel job={job} />

      <section className="panel">
        <h2>My Documents</h2>
        <ul>
          {documents.map((d) => (
            <li key={d.id}>
              <button onClick={() => openDocument(d.id)}>{d.title}</button>
              <small> {d.status} {d.pages ? `(${d.pages} pages)` : ""}</small>
              <button className="btn-delete" onClick={() => handleDelete(d.id)}>Delete</button>
            </li>
          ))}
        </ul>
      </section>

      <DeckEditor deck={deck} onSave={saveDeck} onExport={downloadMarkdown} onExportPptx={downloadPptx} />

      {error ? <p className="error">{error}</p> : null}
    </main>
  );
}
