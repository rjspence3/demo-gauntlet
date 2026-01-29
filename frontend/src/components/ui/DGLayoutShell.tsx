import React from 'react';

export interface DGLayoutShellProps {
  children: React.ReactNode;
}

export function DGLayoutShell({ children }: DGLayoutShellProps) {
  return (
    <div className="min-h-screen bg-[#050505] text-slate-100 font-sans">
      {/* Background grid effect */}
      <div
        className="fixed inset-0 z-0 pointer-events-none opacity-[0.03]"
        style={{
          backgroundImage: `
            linear-gradient(rgba(255,255,255,0.5) 1px, transparent 1px),
            linear-gradient(90deg, rgba(255,255,255,0.5) 1px, transparent 1px)
          `,
          backgroundSize: '50px 50px',
          maskImage: 'radial-gradient(ellipse at center, black 0%, transparent 70%)',
          WebkitMaskImage: 'radial-gradient(ellipse at center, black 0%, transparent 70%)',
        }}
      />

      {/* Content wrapper - above background */}
      <div className="relative z-10">
        {children}
      </div>
    </div>
  );
}
