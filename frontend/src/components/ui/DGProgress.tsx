import React from 'react';
import { cn } from '../../lib/utils';

export interface DGProgressProps {
  value: number;
  variant?: 'default' | 'success' | 'warning' | 'danger' | 'ai';
  size?: 'sm' | 'md';
  className?: string;
}

export function DGProgress({
  value,
  variant = 'default',
  size = 'md',
  className,
}: DGProgressProps) {
  const variantClasses = {
    default: 'bg-brand-500',
    success: 'bg-status-success',
    warning: 'bg-status-warning',
    danger: 'bg-status-error',
    ai: 'bg-gradient-to-r from-ai-500 to-ai-400',
  };

  const sizeClasses = {
    sm: 'h-1',
    md: 'h-1.5',
  };

  return (
    <div
      className={cn(
        'w-full bg-black/5 rounded-full overflow-hidden',
        sizeClasses[size],
        className
      )}
    >
      <div
        className={cn(
          'h-full rounded-full transition-all duration-500',
          variantClasses[variant]
        )}
        style={{ width: `${Math.min(Math.max(value, 0), 100)}%` }}
      />
    </div>
  );
}
