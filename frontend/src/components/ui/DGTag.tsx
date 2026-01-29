import React from 'react';
import { cn } from '../../lib/utils';

export interface DGTagProps {
  variant?: 'default' | 'accent';
  children: React.ReactNode;
  className?: string;
}

export function DGTag({
  variant = 'default',
  children,
  className,
}: DGTagProps) {
  const variantClasses = {
    default: 'bg-slate-800 text-slate-300 border border-slate-700/50',
    accent: 'bg-cyan-400/10 text-cyan-400 border border-cyan-400/20',
  };

  return (
    <span
      className={cn(
        'inline-flex items-center px-3 py-1 rounded-full text-xs font-medium',
        variantClasses[variant],
        className
      )}
    >
      {children}
    </span>
  );
}
