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
    'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#0176D3]/40 focus-visible:ring-offset-2 focus-visible:ring-offset-[#002E50]'
  );

  const variantClasses = {
    primary: 'bg-[#0176D3] text-white hover:bg-[#0264B0] active:bg-[#014D89] shadow-sm hover:shadow-md',
    secondary: 'border border-white/20 text-white hover:bg-white/10 hover:border-white/30',
    ghost: 'bg-transparent text-white/60 hover:bg-white/10 hover:text-white',
    danger: 'bg-[#BA0517] text-white hover:bg-[#9A0413]',
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
