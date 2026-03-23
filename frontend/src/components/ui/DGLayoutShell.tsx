import React from 'react';

export interface DGLayoutShellProps {
  children: React.ReactNode;
}

export function DGLayoutShell({ children }: DGLayoutShellProps) {
  return (
    <div className="min-h-screen bg-zinc-50 text-slate-900 font-sans">
      <div className="relative z-10">
        {children}
      </div>
    </div>
  );
}
