import type { Job } from "../types";

type Props = {
  job: Job | null;
};

export function JobStatusPanel({ job }: Props) {
  if (!job) return null;
  return (
    <section className="panel">
      <h2>Job Status</h2>
      <p>Status: {job.status}</p>
      <p>Progress: {Math.round(job.progress * 100)}%</p>
      {job.error_code ? <p className="error">{job.error_code}: {job.error_detail}</p> : null}
    </section>
  );
}
