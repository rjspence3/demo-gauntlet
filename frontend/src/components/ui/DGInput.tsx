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
        <label className="text-sm font-medium text-slate-300 ml-1">
          {label}
        </label>
      )}
      <div className="relative group">
        {icon && (
          <div className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500 group-focus-within:text-cyan-400 transition-colors">
            {icon}
          </div>
        )}
        <input
          className={cn(
            'w-full bg-slate-800/50 border border-slate-700/50 rounded-xl py-3 px-4 text-white placeholder-slate-500',
            'focus:outline-none focus:border-cyan-400/50 focus:ring-1 focus:ring-cyan-400/50 transition-colors',
            icon && 'pl-11',
            error && 'border-rose-500/50 focus:border-rose-500/50 focus:ring-rose-500/50',
            className
          )}
          {...props}
        />
      </div>
      {error && (
        <p className="text-sm text-rose-500 ml-1">{error}</p>
      )}
    </div>
  );
}
