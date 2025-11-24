"use client";

import { ProfileShell } from "@/app/profile/components/ProfileShell";
import { ProfileSidebar } from "@/app/profile/components/ProfileSidebar";
import { ProfileOverview } from "@/app/profile/components/ProfileOverview";
import { ResumeHistory } from "@/app/profile/components/ResumeHistory";
import { useProfileData } from "@/app/profile/hooks/useProfileData";
import { Pill } from "@/components/Pill";
import { SectionHeader } from "@/components/SectionHeader";
import { Callout } from "@/components/Callout";

export default function ProfilePage() {
  const userId = process.env.NEXT_PUBLIC_DEMO_USER_ID || "demo-user";
  const { data, loading, error } = useProfileData(userId);

  return (
    <ProfileShell sidebar={<ProfileSidebar />}>
      <div className="space-y-3">
        <Pill>
          <span className="font-medium text-emerald-300">resuMAX</span>
          <span className="text-white/80">Profile</span>
        </Pill>
        <SectionHeader
          title="Your profile"
          description="Review your info and resume history. Re-upload if you’ve updated your resume."
        />
      </div>

      {error ? <Callout title="Profile" className="mt-2">{error}</Callout> : null}

      {loading || !data ? (
        <Callout title="Loading profile..." className="mt-4">
          Fetching your profile data.
        </Callout>
      ) : (
        <div className="space-y-6">
          <ProfileOverview info={data.info} onReparse={() => { /* TODO: hook into backend re-parse */ }} />
          <ResumeHistory resumes={data.resumes} />
        </div>
      )}
    </ProfileShell>
  );
}
