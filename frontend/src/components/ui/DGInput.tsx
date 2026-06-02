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
        <label className="text-xs font-medium text-white/60 uppercase tracking-wider ml-1">
          {label}
        </label>
      )}
      <div className="relative group">
        {icon && (
          <div className="absolute left-3 top-1/2 -translate-y-1/2 text-white/40 group-focus-within:text-[#0176D3] transition-colors">
            {icon}
          </div>
        )}
        <input
          className={cn(
            'w-full bg-[#0A3D6B]/60 backdrop-blur-sm border border-[#0176D3]/25 rounded-xl py-2.5 px-3 text-white placeholder-white/40 text-sm',
            'focus:outline-none focus:border-[#0176D3]/60 focus:ring-2 focus:ring-[#0176D3]/20 transition-all',
            icon && 'pl-10',
            error && 'border-[#BA0517]/50 focus:border-[#BA0517]/50 focus:ring-[#BA0517]/20',
            className
          )}
          {...props}
        />
      </div>
      {error && (
        <p className="text-xs text-[#BA0517] ml-1">{error}</p>
      )}
    </div>
  );
}
