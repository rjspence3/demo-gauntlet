import React from 'react';
import { cn } from '../../lib/utils';

export interface DGBadgeProps {
  variant?: 'default' | 'success' | 'warning' | 'danger' | 'ai';
  children: React.ReactNode;
  className?: string;
}

export function DGBadge({
  variant = 'default',
  children,
  className,
}: DGBadgeProps) {
  const variantClasses = {
    default: 'bg-white/10 text-white/80 border border-white/15',
    success: 'bg-[#2E844A]/15 text-[#4CAF50] border border-[#2E844A]/25',
    warning: 'bg-[#FE9339]/15 text-[#FE9339] border border-[#FE9339]/25',
    danger: 'bg-[#BA0517]/15 text-[#EF5350] border border-[#BA0517]/25',
    ai: 'bg-[#0176D3]/15 text-[#3392DF] border border-[#0176D3]/25',
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
