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
    'inline-flex items-center justify-center rounded-full transition-colors',
    'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-orange-500 focus-visible:ring-offset-2 focus-visible:ring-offset-white',
    'disabled:opacity-40 disabled:cursor-not-allowed'
  );

  const sizeClasses = {
    sm: 'w-9 h-9 min-w-[36px] min-h-[36px]',
    md: 'w-11 h-11 min-w-[44px] min-h-[44px]',
  };

  const variantClasses = {
    default: 'text-slate-500 hover:text-slate-900 hover:bg-slate-100',
    active: 'text-orange-500 bg-orange-50 hover:bg-orange-100',
    danger: 'text-rose-500 hover:text-rose-600 hover:bg-rose-50',
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
        <span className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 px-2 py-1 text-xs font-medium text-white bg-slate-800 rounded opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap pointer-events-none z-50">
          {tooltip}
        </span>
      </span>
    );
  }

  return button;
}
