import { Loader2, AlertCircle } from "lucide-react";

import { Progress } from "@/components/ui/progress";
import { ErrorAlert } from "@/components/shared/ErrorAlert";
import type { Job } from "@/types";

interface ProcessingStateProps {
  job: Job;
  error: string;
  onDismissError: () => void;
}

const PIPELINE_STEPS = [
  { threshold: 0, label: "Uploading document..." },
  { threshold: 5, label: "Parsing PDF text and images..." },
  { threshold: 15, label: "Detecting language..." },
  { threshold: 20, label: "Extracting images..." },
  { threshold: 30, label: "Detecting formulas..." },
  { threshold: 40, label: "Extracting facts with LLM..." },
  { threshold: 60, label: "Deduplicating facts..." },
  { threshold: 65, label: "Building outline..." },
  { threshold: 75, label: "Writing annotations..." },
  { threshold: 85, label: "Aligning citations..." },
  { threshold: 95, label: "Persisting results..." },
];

function getCurrentStep(progress: number): string {
  let step = PIPELINE_STEPS[0].label;
  for (const s of PIPELINE_STEPS) {
    if (progress >= s.threshold) {
      step = s.label;
    }
  }
  return step;
}

export function ProcessingState({ job, error, onDismissError }: ProcessingStateProps) {
  const isFailed = job.status === "failed";
  const isActive = job.status === "queued" || job.status === "running";

  return (
    <div className="flex h-full flex-col items-center justify-center gap-6 px-8">
      <div className="flex w-full max-w-sm flex-col items-center gap-5">
        {/* Icon */}
        {isFailed ? (
          <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-destructive/10">
            <AlertCircle className="h-6 w-6 text-destructive" />
          </div>
        ) : (
          <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-primary/10 glow-sm">
            <Loader2 className="h-6 w-6 animate-spin text-primary" />
          </div>
        )}

        {/* Title + current step */}
        <div className="text-center">
          <h2 className="text-base font-semibold">
            {isFailed ? "Processing Failed" : "Processing Document"}
          </h2>
          {isActive && (
            <p className="mt-1.5 text-sm text-muted-foreground animate-in fade-in-50 duration-300">
              {getCurrentStep(job.progress)}
            </p>
          )}
          {isFailed && (
            <p className="mt-1.5 text-sm text-muted-foreground">
              {job.error_detail || "An error occurred during processing."}
            </p>
          )}
        </div>

        {/* Progress bar */}
        {isActive && (
          <div className="w-full space-y-2">
            <Progress value={job.progress} className="h-2" />
            <div className="flex items-center justify-between text-xs text-muted-foreground">
              <span>{Math.round(job.progress)}%</span>
              <span className="capitalize">{job.status}</span>
            </div>
          </div>
        )}

        {/* Pipeline step list */}
        {isActive && (
          <div className="w-full space-y-1.5 pt-2">
            {PIPELINE_STEPS.map((step) => {
              const isDone = job.progress > step.threshold;
              const isCurrent =
                job.progress >= step.threshold &&
                (PIPELINE_STEPS.indexOf(step) === PIPELINE_STEPS.length - 1 ||
                  job.progress < PIPELINE_STEPS[PIPELINE_STEPS.indexOf(step) + 1].threshold);

              return (
                <div
                  key={step.threshold}
                  className={`
                    flex items-center gap-2 text-xs transition-all duration-300
                    ${isCurrent ? "text-foreground font-medium translate-x-1" : isDone ? "text-muted-foreground" : "text-muted-foreground/30"}
                  `}
                >
                  <span className="flex h-4 w-4 shrink-0 items-center justify-center">
                    {isDone && !isCurrent ? (
                      <svg className="h-3 w-3 text-primary animate-check-appear" viewBox="0 0 12 12" fill="none">
                        <path d="M2 6l3 3 5-5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
                      </svg>
                    ) : isCurrent ? (
                      <Loader2 className="h-3 w-3 animate-spin text-primary" />
                    ) : (
                      <span className="h-1.5 w-1.5 rounded-full bg-current opacity-40" />
                    )}
                  </span>
                  {step.label.replace("...", "")}
                </div>
              );
            })}
          </div>
        )}

        {/* Error code badge */}
        {isFailed && job.error_code && (
          <p className="rounded-md bg-muted px-3 py-1.5 text-xs font-mono text-muted-foreground">
            {job.error_code}
          </p>
        )}
      </div>

      {error && (
        <div className="w-full max-w-sm">
          <ErrorAlert message={error} onDismiss={onDismissError} />
        </div>
      )}
    </div>
  );
}
