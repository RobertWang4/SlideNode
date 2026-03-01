import { Badge } from "@/components/ui/badge";

interface BulletItemProps {
  bulletId: string;
  text: string;
  citationCount: number;
  isActive: boolean;
  onTextChange: (text: string) => void;
  onFocus: () => void;
}

export function BulletItem({
  bulletId,
  text,
  citationCount,
  isActive,
  onTextChange,
  onFocus,
}: BulletItemProps) {
  return (
    <div
      className={`
        group flex items-start gap-2 rounded-lg px-2.5 py-2
        transition-all duration-200
        ${isActive ? "bg-primary/6 shadow-sm shadow-primary/5" : "hover:bg-muted/50"}
      `}
    >
      <span className={`
        mt-2 h-1.5 w-1.5 shrink-0 rounded-full transition-colors duration-200
        ${isActive ? "bg-primary" : "bg-foreground/25"}
      `} />
      <input
        type="text"
        value={text}
        onChange={(e) => onTextChange(e.target.value)}
        onFocus={onFocus}
        className={`
          flex-1 bg-transparent text-sm leading-relaxed outline-none
          transition-colors duration-150
          placeholder:text-muted-foreground
          ${isActive ? "text-foreground" : "text-foreground/80"}
        `}
      />
      <Badge
        variant="outline"
        className={`
          shrink-0 text-[10px] font-mono cursor-default transition-all duration-200
          ${isActive ? "border-primary/30 bg-primary/5 text-primary" : "text-muted-foreground/60 border-border/50"}
        `}
      >
        {citationCount}
      </Badge>
    </div>
  );
}
