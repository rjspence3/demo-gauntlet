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
    default: 'bg-white/10 text-white/60 border border-white/12',
    accent: 'bg-[#0176D3]/15 text-[#3392DF] border border-[#0176D3]/25',
  };

  return (
    <span
      className={cn(
        'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium',
        variantClasses[variant],
        className
      )}
    >
      {children}
    </span>
  );
}
