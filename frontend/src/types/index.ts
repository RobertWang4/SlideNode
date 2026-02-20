export type Citation = {
  page: number;
  paragraph_index: number;
  quote_snippet: string;
};

export type Bullet = {
  id: string;
  text: string;
  citations: Citation[];
};

export type Subsection = {
  id: string;
  heading: string;
  annotation: string;
  bullets: Bullet[];
};

export type Section = {
  id: string;
  heading: string;
  summary_note: string;
  subsections: Subsection[];
};

export type Deck = {
  document_id: string;
  title: string;
  language: string | null;
  quality_report: {
    coverage_ratio: number;
    citation_completeness: number;
    dedupe_ratio: number;
  };
  sections: Section[];
};

export type Job = {
  id: string;
  status: "queued" | "running" | "failed" | "done";
  progress: number;
  error_code: string | null;
  error_detail: string | null;
};

export type DocumentListItem = {
  id: string;
  title: string;
  status: string;
  pages: number | null;
  created_at: string;
};
