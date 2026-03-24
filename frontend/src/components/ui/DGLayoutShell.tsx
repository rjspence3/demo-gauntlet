import React from 'react';

export interface DGLayoutShellProps {
  children: React.ReactNode;
}

export function DGLayoutShell({ children }: DGLayoutShellProps) {
  return (
    <div className="min-h-screen bg-page text-text-primary font-sans flex flex-col">
      <div className="relative z-10 flex flex-col flex-1">
        {children}
      </div>
    </div>
  );
}
