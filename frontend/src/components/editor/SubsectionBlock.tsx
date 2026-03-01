import { MessageSquare } from "lucide-react";

import { BulletItem } from "@/components/editor/BulletItem";
import type { Subsection } from "@/types";

interface SubsectionBlockProps {
  sectionId: string;
  subsection: Subsection;
  draftHeading: string;
  draftAnnotation: string;
  draftBullets: { id: string; text: string }[];
  activeBulletId: string | null;
  onHeadingChange: (heading: string) => void;
  onAnnotationChange: (annotation: string) => void;
  onBulletTextChange: (bulletId: string, text: string) => void;
  onBulletFocus: (bulletId: string) => void;
}

export function SubsectionBlock({
  sectionId,
  subsection,
  draftHeading,
  draftAnnotation,
  draftBullets,
  activeBulletId,
  onHeadingChange,
  onAnnotationChange,
  onBulletTextChange,
  onBulletFocus,
}: SubsectionBlockProps) {
  return (
    <div className="space-y-2">
      <input
        type="text"
        value={draftHeading}
        onChange={(e) => onHeadingChange(e.target.value)}
        className="w-full bg-transparent text-sm font-medium outline-none placeholder:text-muted-foreground"
        placeholder="Subsection heading"
      />

      {/* Annotation */}
      {(draftAnnotation || true) && (
        <div className="flex items-start gap-1.5 pl-1">
          <MessageSquare className="mt-0.5 h-3 w-3 shrink-0 text-muted-foreground/60" />
          <input
            type="text"
            value={draftAnnotation}
            onChange={(e) => onAnnotationChange(e.target.value)}
            className="flex-1 bg-transparent text-xs text-muted-foreground outline-none italic"
            placeholder="Teaching note..."
          />
        </div>
      )}

      {/* Bullets */}
      <div className="space-y-0.5 pl-1">
        {draftBullets.map((bullet, idx) => {
          const originalBullet = subsection.bullets[idx];
          return (
            <BulletItem
              key={bullet.id}
              bulletId={bullet.id}
              text={bullet.text}
              citationCount={originalBullet?.citations?.length ?? 0}
              isActive={bullet.id === activeBulletId}
              onTextChange={(text) => onBulletTextChange(bullet.id, text)}
              onFocus={() => onBulletFocus(bullet.id)}
            />
          );
        })}
      </div>
    </div>
  );
}
