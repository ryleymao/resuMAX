import { useEffect, useState } from "react";
import { listResumes, type ResumeMetadata } from "@/lib/api";
import type { ProfileData } from "../lib/profile";
import { getMockProfileData } from "@/mocks/profile";
import { auth } from "@/lib/firebase/client";

export function useProfileData(userId?: string) {
  const [data, setData] = useState<ProfileData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const useMock = process.env.NEXT_PUBLIC_USE_MOCK_API === "true";

  useEffect(() => {
    let cancelled = false;

    async function load() {
      setLoading(true);
      setError(null);

      try {
        if (!userId || useMock) {
          const mock = getMockProfileData();
          if (!cancelled) {
            setData(mock);
            setLoading(false);
          }
          return;
        }

        const resumes: ResumeMetadata[] = await listResumes(userId);
        const user = auth.currentUser;

        if (!cancelled) {
          setData({
            info: {
              name: user?.displayName || "User",
              email: user?.email || "unknown",
            },
            resumes,
          });
          setLoading(false);
        }
      } catch (err: any) {
        console.error("[profile] failed to load profile", err);
        if (!cancelled) {
          setData(getMockProfileData());
          setError(err?.message || "Failed to load profile");
          setLoading(false);
        }
      }
    }

    load();
    return () => {
      cancelled = true;
    };
  }, [userId, useMock]);

  return { data, loading, error };
}
