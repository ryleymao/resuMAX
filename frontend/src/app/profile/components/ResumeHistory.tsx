import { Card } from "@/components/Card";
import type { ResumeMetadata } from "@/lib/api";

type Props = {
  resumes: ResumeMetadata[];
};

export function ResumeHistory({ resumes }: Props) {
  return (
    <Card tone="muted" className="space-y-3" id="sources">
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="text-sm font-semibold text-emerald-300">Sources</p>
          <h3 className="text-lg font-semibold">Resume upload history</h3>
        </div>
      </div>
      <div className="space-y-2 text-sm text-white/80">
        {resumes.length === 0 ? (
          <p className="text-white/60">No resumes uploaded yet.</p>
        ) : (
          resumes.slice(0, 5).map((resume) => (
            <div
              key={resume.resumeId}
              className="flex items-center gap-3 rounded-lg border border-white/5 bg-white/5 px-3 py-2"
            >
              <div className="flex flex-col">
                <span className="font-semibold text-white">{resume.originalFileName || resume.resumeId}</span>
                <span className="text-xs text-white/60">
                  Uploaded {resume.uploadedAt?.slice(0, 10) || "N/A"} • Status {resume.status || "unknown"}
                </span>
              </div>
              {resume.relevanceScore ? (
                <span className="ml-auto text-xs font-semibold text-emerald-300">
                  Score {Math.round(resume.relevanceScore)}
                </span>
              ) : null}
            </div>
          ))
        )}
      </div>
    </Card>
  );
}
