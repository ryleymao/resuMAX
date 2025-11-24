import type { ReactNode } from "react";
import { Container } from "@/components/Container";

type WorkspaceShellProps = {
  children: ReactNode;
};

export function WorkspaceShell({ children }: WorkspaceShellProps) {
  return (
    <div className="min-h-screen bg-slate-950 text-white">
      <Container className="min-h-screen space-y-10">
        {children}
      </Container>
    </div>
  );
}
