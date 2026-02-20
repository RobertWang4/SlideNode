import { useMemo, useState } from "react";

import type { Deck } from "../types";

type Props = {
  deck: Deck | null;
  onSave: (payload: unknown) => Promise<void>;
  onExport: () => Promise<void>;
  onExportPptx: () => Promise<void>;
};

export function DeckEditor({ deck, onSave, onExport, onExportPptx }: Props) {
  const [busy, setBusy] = useState(false);

  const draft = useMemo(() => {
    if (!deck) return null;
    return {
      sections: deck.sections.map((s) => ({
        id: s.id,
        heading: s.heading,
        summary_note: s.summary_note,
        subsections: s.subsections.map((ss) => ({
          id: ss.id,
          heading: ss.heading,
          annotation: ss.annotation,
          bullets: ss.bullets.map((b) => ({ id: b.id, text: b.text }))
        }))
      }))
    };
  }, [deck]);

  if (!deck || !draft) return null;

  return (
    <section className="panel deck">
      <div className="panel-row">
        <h2>{deck.title}</h2>
        <div className="actions">
          <button
            disabled={busy}
            onClick={async () => {
              setBusy(true);
              await onSave(draft);
              setBusy(false);
            }}
          >
            Save Edits
          </button>
          <button disabled={busy} onClick={onExport}>Export Markdown</button>
          <button disabled={busy} onClick={onExportPptx}>Export PPTX</button>
        </div>
      </div>
      <p>
        Coverage: {deck.quality_report.coverage_ratio.toFixed(2)} | Citation Completeness:{" "}
        {deck.quality_report.citation_completeness.toFixed(2)}
      </p>
      {deck.sections.map((section) => (
        <article key={section.id} className="section">
          <h3>{section.heading}</h3>
          <p>{section.summary_note}</p>
          {section.subsections.map((ss) => (
            <div key={ss.id} className="subsection">
              <h4>{ss.heading}</h4>
              <p className="note">{ss.annotation}</p>
              <ul>
                {ss.bullets.map((b) => (
                  <li key={b.id}>
                    {b.text}
                    <div className="citations">
                      {b.citations.map((c, idx) => (
                        <small key={idx}>
                          p.{c.page} para {c.paragraph_index}: {c.quote_snippet}
                        </small>
                      ))}
                    </div>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </article>
      ))}
    </section>
  );
}
