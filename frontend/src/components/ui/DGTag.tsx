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
    default: 'bg-white/60 text-text-muted border border-border',
    accent: 'bg-ai-50 text-ai-700 border border-ai-100',
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
