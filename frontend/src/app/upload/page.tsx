"use client";

import { WorkspaceShell } from "@/app/workspace/components/WorkspaceShell";
import { Navbar } from "@/app/workspace/components/Navbar";
import { UploadForm } from "@/app/upload/components/UploadForm";

export default function UploadPage() {
  const userId = process.env.NEXT_PUBLIC_DEMO_USER_ID || "demo-user";

  return (
    <WorkspaceShell>
      <Navbar />
      <div className="max-w-3xl">
        <h1 className="text-2xl font-semibold text-white">Upload your resume</h1>
        <p className="mt-2 text-sm text-white/70">
          Add your PDF to keep your profile current. You can re-upload anytime.
        </p>
      </div>
      <UploadForm userId={userId} />
    </WorkspaceShell>
  );
}
