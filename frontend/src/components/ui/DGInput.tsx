import React from 'react';
import { cn } from '../../lib/utils';

export interface DGInputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  icon?: React.ReactNode;
}

export function DGInput({
  label,
  error,
  icon,
  className,
  ...props
}: DGInputProps) {
  return (
    <div className="space-y-2">
      {label && (
        <label className="text-xs font-medium text-text-muted uppercase tracking-wider ml-1">
          {label}
        </label>
      )}
      <div className="relative group">
        {icon && (
          <div className="absolute left-3 top-1/2 -translate-y-1/2 text-text-faint group-focus-within:text-ai-500 transition-colors">
            {icon}
          </div>
        )}
        <input
          className={cn(
            'w-full bg-white/80 backdrop-blur-sm border border-border-ai rounded-xl py-2.5 px-3 text-text-primary placeholder-text-faint text-sm',
            'focus:outline-none focus:border-ai-400 focus:ring-2 focus:ring-ai-500/20 transition-all',
            icon && 'pl-10',
            error && 'border-status-error/50 focus:border-status-error/50 focus:ring-status-error/20',
            className
          )}
          {...props}
        />
      </div>
      {error && (
        <p className="text-xs text-status-error ml-1">{error}</p>
      )}
    </div>
  );
}
