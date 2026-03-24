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
    'inline-flex items-center justify-center rounded-xl transition-all duration-150',
    'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ai-500/40 focus-visible:ring-offset-2 focus-visible:ring-offset-page',
    'disabled:opacity-40 disabled:cursor-not-allowed'
  );

  const sizeClasses = {
    sm: 'w-8 h-8 min-w-[32px] min-h-[32px]',
    md: 'w-10 h-10 min-w-[40px] min-h-[40px]',
  };

  const variantClasses = {
    default: 'text-text-muted hover:text-text-primary hover:bg-ai-50',
    active: 'text-ai-500 bg-ai-50 hover:bg-ai-100',
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
        <span className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 px-2.5 py-1 text-xs font-medium text-text-primary bg-white border border-border-ai rounded-lg shadow-glass opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap pointer-events-none z-50">
          {tooltip}
        </span>
      </span>
    );
  }

  return button;
}
