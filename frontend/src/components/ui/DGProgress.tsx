import React from 'react';
import { cn } from '../../lib/utils';

export interface DGProgressProps {
  value: number; // 0-100
  variant?: 'default' | 'success' | 'warning' | 'danger';
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
    default: 'bg-cyan-400',
    success: 'bg-emerald-400',
    warning: 'bg-amber-400',
    danger: 'bg-rose-500',
  };

  const sizeClasses = {
    sm: 'h-1.5',
    md: 'h-2',
  };

  return (
    <div
      className={cn(
        'w-full bg-slate-800 rounded-full overflow-hidden',
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
