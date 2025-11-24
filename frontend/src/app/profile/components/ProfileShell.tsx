import type { ReactNode } from "react";
import { WorkspaceShell } from "@/app/workspace/components/WorkspaceShell";
import { Navbar } from "@/app/workspace/components/Navbar";

export function ProfileShell({ children, sidebar }: { children: ReactNode; sidebar: ReactNode }) {
  return (
    <WorkspaceShell>
      <Navbar />
      <div className="grid gap-8 lg:grid-cols-[260px_1fr]">
        <aside className="space-y-3 rounded-2xl border border-white/10 bg-white/5 p-4">
          {sidebar}
        </aside>
        <section className="space-y-4">{children}</section>
      </div>
    </WorkspaceShell>
  );
}
