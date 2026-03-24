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
    default: 'bg-surface-overlay text-text-secondary border border-border',
    success: 'bg-status-success/10 text-status-success border border-status-success/20',
    warning: 'bg-status-warning/10 text-status-warning border border-status-warning/20',
    danger: 'bg-status-error/10 text-status-error border border-status-error/20',
  };

  return (
    <span
      className={cn(
        'inline-flex items-center px-2 py-0.5 rounded-md text-xs font-medium',
        variantClasses[variant],
        className
      )}
    >
      {children}
    </span>
  );
}
