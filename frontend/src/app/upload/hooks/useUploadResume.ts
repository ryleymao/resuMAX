import { useState } from "react";
import { uploadResume } from "@/lib/api";
import { uploadResumeMock } from "@/mocks/api";

type UploadResult = {
  resumeId: string;
  originalUrl?: string;
  optimizedUrl?: string;
};

export function useUploadResume(userId?: string) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<UploadResult | null>(null);
  const useMock = process.env.NEXT_PUBLIC_USE_MOCK_API === "true";

  async function handleUpload(file: File): Promise<UploadResult | null> {
    if (!userId) {
      setError("User not available");
      return null;
    }
    setError(null);
    setLoading(true);
    setResult(null);

    try {
      const uploadRes = useMock
        ? await uploadResumeMock({ userId, file })
        : await uploadResume({ userId, file });

      const resumeId = uploadRes.resume_id || uploadRes.resumeId || "unknown";
      const uploadResult: UploadResult = {
        resumeId,
        originalUrl: uploadRes.original_file_url,
        optimizedUrl: uploadRes.optimized_file_url,
      };

      setResult(uploadResult);
      return uploadResult;
    } catch (err: any) {
      setError(err?.message || "Failed to upload resume");
      return null;
    } finally {
      setLoading(false);
    }
  }

  return { loading, error, result, handleUpload };
}
