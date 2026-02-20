import type { Deck, DocumentListItem, Job } from "../types";

const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/v1";
const RAW_TOKEN = (import.meta.env.VITE_BEARER_TOKEN || "").trim();
const TOKEN = RAW_TOKEN === "replace_with_auth0_access_token_for_dev" ? "" : RAW_TOKEN;

function headers(extra?: HeadersInit): HeadersInit {
  const base: Record<string, string> = {};
  if (TOKEN) {
    base.Authorization = `Bearer ${TOKEN}`;
  }
  return {
    ...base,
    ...extra
  };
}

export async function uploadDocument(file: File): Promise<{ document_id: string; job_id: string }> {
  const form = new FormData();
  form.append("file", file);
  const res = await fetch(`${API_BASE}/documents`, {
    method: "POST",
    headers: headers(),
    body: form
  });
  if (!res.ok) {
    throw new Error(await res.text());
  }
  return res.json();
}

export async function getJob(jobId: string): Promise<Job> {
  const res = await fetch(`${API_BASE}/jobs/${jobId}`, { headers: headers() });
  if (!res.ok) {
    throw new Error(await res.text());
  }
  return res.json();
}

export async function listDocuments(): Promise<DocumentListItem[]> {
  const res = await fetch(`${API_BASE}/documents`, { headers: headers() });
  if (!res.ok) {
    throw new Error(await res.text());
  }
  const body = await res.json();
  return body.items as DocumentListItem[];
}

export async function getDeck(documentId: string): Promise<Deck> {
  const res = await fetch(`${API_BASE}/documents/${documentId}/slides`, { headers: headers() });
  if (!res.ok) {
    throw new Error(await res.text());
  }
  return res.json();
}

export async function patchDeck(documentId: string, payload: unknown): Promise<Deck> {
  const res = await fetch(`${API_BASE}/documents/${documentId}/slides`, {
    method: "PATCH",
    headers: headers({ "Content-Type": "application/json" }),
    body: JSON.stringify(payload)
  });
  if (!res.ok) {
    throw new Error(await res.text());
  }
  return res.json();
}

export async function exportMarkdown(documentId: string): Promise<string> {
  const res = await fetch(`${API_BASE}/documents/${documentId}/export.md`, { headers: headers() });
  if (!res.ok) {
    throw new Error(await res.text());
  }
  return res.text();
}

export async function deleteDocument(documentId: string): Promise<void> {
  const res = await fetch(`${API_BASE}/documents/${documentId}`, {
    method: "DELETE",
    headers: headers(),
  });
  if (!res.ok) {
    throw new Error(await res.text());
  }
}

export async function exportPptx(documentId: string): Promise<Blob> {
  const res = await fetch(`${API_BASE}/documents/${documentId}/export.pptx`, { headers: headers() });
  if (!res.ok) {
    throw new Error(await res.text());
  }
  return res.blob();
}
