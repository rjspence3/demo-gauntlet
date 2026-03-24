import React from 'react';
import { cn } from '../../lib/utils';
import { Loader2 } from 'lucide-react';

export interface DGButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'ghost' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  loading?: boolean;
  children: React.ReactNode;
}

export function DGButton({
  variant = 'primary',
  size = 'md',
  loading = false,
  disabled,
  className,
  children,
  ...props
}: DGButtonProps) {
  const baseClasses = cn(
    'inline-flex items-center justify-center gap-2 font-semibold transition-all duration-200 rounded-xl',
    'disabled:opacity-40 disabled:cursor-not-allowed',
    'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ai-500/40 focus-visible:ring-offset-2 focus-visible:ring-offset-page'
  );

  const variantClasses = {
    primary: 'bg-brand-500 text-white hover:bg-brand-600 active:bg-brand-700 shadow-sm hover:shadow-md',
    secondary: 'bg-white/80 backdrop-blur-sm border border-border-ai text-text-secondary hover:bg-white hover:border-ai-300 hover:text-text-primary',
    ghost: 'bg-transparent text-text-muted hover:bg-ai-50 hover:text-ai-600',
    danger: 'bg-status-error/10 text-status-error border border-status-error/20 hover:bg-status-error/20',
  };

  const sizeClasses = {
    sm: 'px-3.5 py-1.5 text-xs',
    md: 'px-5 py-2.5 text-sm',
    lg: 'px-7 py-3 text-sm',
  };

  return (
    <button
      className={cn(baseClasses, variantClasses[variant], sizeClasses[size], className)}
      disabled={disabled || loading}
      {...props}
    >
      {loading ? (
        <>
          <Loader2 className="w-4 h-4 animate-spin" />
          <span>Loading...</span>
        </>
      ) : (
        children
      )}
    </button>
  );
}
