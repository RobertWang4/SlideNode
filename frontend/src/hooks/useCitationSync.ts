import { useCallback, useMemo, useState } from "react";

import type { Citation, Deck } from "@/types";

export function useCitationSync(deck: Deck | null) {
  const [activeBulletId, setActiveBulletId] = useState<string | null>(null);

  const activeCitations = useMemo<Citation[]>(() => {
    if (!deck || !activeBulletId) return [];
    for (const section of deck.sections) {
      for (const sub of section.subsections) {
        for (const bullet of sub.bullets) {
          if (bullet.id === activeBulletId) {
            return bullet.citations;
          }
        }
      }
    }
    return [];
  }, [deck, activeBulletId]);

  const handleBulletFocus = useCallback((bulletId: string) => {
    setActiveBulletId(bulletId);
  }, []);

  const clearActiveBullet = useCallback(() => {
    setActiveBulletId(null);
  }, []);

  return {
    activeBulletId,
    activeCitations,
    handleBulletFocus,
    clearActiveBullet,
  };
}
