import { useRouter } from "next/navigation";
import { useState } from "react";
import { Button } from "@/components/Button";
import { Card } from "@/components/Card";
import { useUploadResume } from "../hooks/useUploadResume";

type UploadFormProps = {
  userId: string;
};

export function UploadForm({ userId }: UploadFormProps) {
  const { loading, error, result, handleUpload } = useUploadResume(userId);
  const router = useRouter();
  const [file, setFile] = useState<File | null>(null);

  return (
    <Card tone="neutral" className="space-y-4">
      <form
        className="space-y-4"
        onSubmit={(e) => {
          e.preventDefault();
          if (!file) return;
          handleUpload(file).then((res) => {
            if (res?.resumeId) {
              router.push(`/profile?resumeId=${encodeURIComponent(res.resumeId)}`);
            }
          });
        }}
      >
        <div className="space-y-2">
          <label className="text-sm font-medium text-white/90" htmlFor="resume">
            Resume file (PDF)
          </label>
          <input
            id="resume"
            name="resume"
            type="file"
            accept=".pdf,application/pdf"
            className="w-full rounded-xl border border-white/12 bg-white/5 px-4 py-3 text-white placeholder:text-white/50 focus:border-emerald-300 focus:outline-none focus:ring-2 focus:ring-emerald-300/30"
            disabled={loading}
            onChange={(e) => {
              const picked = e.target.files?.[0] || null;
              setFile(picked);
            }}
          />
          {file ? (
            <p className="text-sm text-white/70">Selected: {file.name}</p>
          ) : (
            <p className="text-sm text-white/50">Max 10MB. Accepted: PDF only.</p>
          )}
        </div>

        {error ? <p className="text-sm text-rose-300">{error}</p> : null}

        <Button type="submit" className="w-full" disabled={!file || loading}>
          {loading ? "Uploading..." : "Upload"}
        </Button>
      </form>

      {result ? (
        <div className="rounded-xl border border-white/10 bg-white/5 p-4 text-sm text-white/80">
          <p className="font-semibold text-white">Upload complete</p>
          <p className="mt-1">Resume ID: {result.resumeId}</p>
          {result.originalUrl ? (
            <p className="mt-1">
              Original: <span className="text-emerald-200">{result.originalUrl}</span>
            </p>
          ) : null}
          {result.optimizedUrl ? (
            <p className="mt-1">
              Optimized: <span className="text-emerald-200">{result.optimizedUrl}</span>
            </p>
          ) : (
            <p className="mt-1 text-white/60">No optimization requested.</p>
          )}
        </div>
      ) : null}
    </Card>
  );
}
