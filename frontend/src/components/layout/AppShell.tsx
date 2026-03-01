import type { ReactNode } from "react";

interface AppShellProps {
  sidebar: ReactNode;
  children: ReactNode;
}

export function AppShell({ sidebar, children }: AppShellProps) {
  return (
    <div className="flex h-screen w-screen overflow-hidden bg-[hsl(var(--sidebar-bg))]">
      {sidebar}
      <main className="flex-1 overflow-hidden">{children}</main>
    </div>
  );
}
