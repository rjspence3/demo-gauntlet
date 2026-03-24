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
    default: 'bg-surface-overlay text-text-muted border border-border',
    accent: 'bg-brand-500/10 text-brand-400 border border-brand-500/20',
  };

  return (
    <span
      className={cn(
        'inline-flex items-center px-2.5 py-0.5 rounded-md text-xs font-medium',
        variantClasses[variant],
        className
      )}
    >
      {children}
    </span>
  );
}
