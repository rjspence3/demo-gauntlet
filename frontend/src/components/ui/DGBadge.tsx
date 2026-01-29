import React from 'react';
import { cn } from '../../lib/utils';

export interface DGBadgeProps {
  variant?: 'default' | 'success' | 'warning' | 'danger';
  children: React.ReactNode;
  className?: string;
}

export function DGBadge({
  variant = 'default',
  children,
  className,
}: DGBadgeProps) {
  const variantClasses = {
    default: 'bg-slate-700/50 text-slate-300',
    success: 'bg-emerald-400/10 text-emerald-400',
    warning: 'bg-amber-400/10 text-amber-400',
    danger: 'bg-rose-500/10 text-rose-500',
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
