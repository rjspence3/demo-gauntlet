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
    default: 'bg-[#0176D3]',
    success: 'bg-[#2E844A]',
    warning: 'bg-[#FE9339]',
    danger: 'bg-[#BA0517]',
    ai: 'bg-gradient-to-r from-[#0176D3] to-[#3392DF]',
  };

  const sizeClasses = {
    sm: 'h-1',
    md: 'h-1.5',
  };

  return (
    <div
      className={cn(
        'w-full bg-white/10 rounded-full overflow-hidden',
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
