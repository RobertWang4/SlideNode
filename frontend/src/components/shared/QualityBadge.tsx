import { Badge } from "@/components/ui/badge";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";

interface QualityBadgeProps {
  label: string;
  value: number;
  threshold?: number;
}

export function QualityBadge({ label, value, threshold = 0.85 }: QualityBadgeProps) {
  const percent = Math.round(value * 100);
  const isGood = value >= threshold;

  return (
    <TooltipProvider>
      <Tooltip>
        <TooltipTrigger asChild>
          <Badge
            variant={isGood ? "secondary" : "destructive"}
            className={`
              cursor-default text-[11px] font-medium transition-all duration-200
              ${isGood
                ? "bg-emerald-50 text-emerald-700 border-emerald-200/60 shadow-sm shadow-emerald-100"
                : "bg-red-50 text-red-700 border-red-200/60 shadow-sm shadow-red-100"
              }
            `}
          >
            {label} {percent}%
          </Badge>
        </TooltipTrigger>
        <TooltipContent>
          <p>{label}: {percent}% {isGood ? "(passing)" : `(below ${Math.round(threshold * 100)}%)`}</p>
        </TooltipContent>
      </Tooltip>
    </TooltipProvider>
  );
}
