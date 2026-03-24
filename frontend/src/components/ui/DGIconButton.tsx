import React from 'react';
import { cn } from '../../lib/utils';

export interface DGIconButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  icon: React.ReactNode;
  ariaLabel: string;
  tooltip?: string;
  variant?: 'default' | 'active' | 'danger';
  size?: 'sm' | 'md';
}

export function DGIconButton({
  icon,
  ariaLabel,
  tooltip,
  variant = 'default',
  size = 'md',
  disabled,
  className,
  ...props
}: DGIconButtonProps) {
  const baseClasses = cn(
    'inline-flex items-center justify-center rounded-lg transition-colors',
    'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-500/50 focus-visible:ring-offset-2 focus-visible:ring-offset-white',
    'disabled:opacity-40 disabled:cursor-not-allowed'
  );

  const sizeClasses = {
    sm: 'w-8 h-8 min-w-[32px] min-h-[32px]',
    md: 'w-10 h-10 min-w-[40px] min-h-[40px]',
  };

  const variantClasses = {
    default: 'text-text-muted hover:text-text-primary hover:bg-surface-elevated',
    active: 'text-brand-500 bg-brand-500/10 hover:bg-brand-500/20',
    danger: 'text-status-error hover:text-status-error hover:bg-status-error/10',
  };

  const button = (
    <button
      type="button"
      disabled={disabled}
      aria-label={ariaLabel}
      className={cn(baseClasses, sizeClasses[size], variantClasses[variant], className)}
      {...props}
    >
      {icon}
    </button>
  );

  if (tooltip) {
    return (
      <span className="relative group">
        {button}
        <span className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 px-2 py-1 text-xs font-medium text-text-primary bg-surface-overlay border border-border rounded-md opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap pointer-events-none z-50">
          {tooltip}
        </span>
      </span>
    );
  }

  return button;
}
