import { useCallback, useEffect, useRef, useState } from "react";

import type { Deck, Section } from "@/types";

export interface DraftSection {
  id: string;
  heading: string;
  subsections: {
    id: string;
    heading: string;
    annotation: string;
    bullets: {
      id: string;
      text: string;
    }[];
  }[];
}

export function useDeckDraft(deck: Deck | null) {
  const [draftSections, setDraftSections] = useState<DraftSection[]>([]);
  const [isDirty, setIsDirty] = useState(false);
  const deckIdRef = useRef<string | null>(null);

  // Reset draft when deck changes
  useEffect(() => {
    if (!deck) {
      setDraftSections([]);
      setIsDirty(false);
      deckIdRef.current = null;
      return;
    }

    if (deckIdRef.current !== deck.document_id) {
      deckIdRef.current = deck.document_id;
      setDraftSections(sectionsToSraft(deck.sections));
      setIsDirty(false);
    }
  }, [deck]);

  const updateSectionHeading = useCallback((sectionId: string, heading: string) => {
    setDraftSections((prev) =>
      prev.map((s) => (s.id === sectionId ? { ...s, heading } : s))
    );
    setIsDirty(true);
  }, []);

  const updateSubsectionHeading = useCallback(
    (sectionId: string, subsectionId: string, heading: string) => {
      setDraftSections((prev) =>
        prev.map((s) =>
          s.id === sectionId
            ? {
                ...s,
                subsections: s.subsections.map((sub) =>
                  sub.id === subsectionId ? { ...sub, heading } : sub
                ),
              }
            : s
        )
      );
      setIsDirty(true);
    },
    []
  );

  const updateSubsectionAnnotation = useCallback(
    (sectionId: string, subsectionId: string, annotation: string) => {
      setDraftSections((prev) =>
        prev.map((s) =>
          s.id === sectionId
            ? {
                ...s,
                subsections: s.subsections.map((sub) =>
                  sub.id === subsectionId ? { ...sub, annotation } : sub
                ),
              }
            : s
        )
      );
      setIsDirty(true);
    },
    []
  );

  const updateBulletText = useCallback(
    (sectionId: string, subsectionId: string, bulletId: string, text: string) => {
      setDraftSections((prev) =>
        prev.map((s) =>
          s.id === sectionId
            ? {
                ...s,
                subsections: s.subsections.map((sub) =>
                  sub.id === subsectionId
                    ? {
                        ...sub,
                        bullets: sub.bullets.map((b) =>
                          b.id === bulletId ? { ...b, text } : b
                        ),
                      }
                    : sub
                ),
              }
            : s
        )
      );
      setIsDirty(true);
    },
    []
  );

  const getDraftPayload = useCallback(() => {
    return {
      sections: draftSections.map((s) => ({
        id: s.id,
        heading: s.heading,
        subsections: s.subsections.map((sub) => ({
          id: sub.id,
          heading: sub.heading,
          annotation: sub.annotation,
          bullets: sub.bullets.map((b) => ({
            id: b.id,
            text: b.text,
          })),
        })),
      })),
    };
  }, [draftSections]);

  const resetDraft = useCallback(() => {
    if (deck) {
      setDraftSections(sectionsToSraft(deck.sections));
      setIsDirty(false);
    }
  }, [deck]);

  return {
    draftSections,
    isDirty,
    updateSectionHeading,
    updateSubsectionHeading,
    updateSubsectionAnnotation,
    updateBulletText,
    getDraftPayload,
    resetDraft,
  };
}

function sectionsToSraft(sections: Section[]): DraftSection[] {
  return sections.map((s) => ({
    id: s.id,
    heading: s.heading,
    subsections: s.subsections.map((sub) => ({
      id: sub.id,
      heading: sub.heading,
      annotation: sub.annotation,
      bullets: sub.bullets.map((b) => ({
        id: b.id,
        text: b.text,
      })),
    })),
  }));
}
