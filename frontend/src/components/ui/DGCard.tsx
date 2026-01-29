import React from 'react';
import { cn } from '../../lib/utils';

export interface DGCardProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: 'default' | 'elevated' | 'bordered';
  children: React.ReactNode;
}

export function DGCard({
  variant = 'default',
  className,
  children,
  ...props
}: DGCardProps) {
  const variantClasses = {
    default: 'bg-slate-900/70 backdrop-blur-md border border-slate-700/50',
    elevated: 'bg-slate-900 border border-slate-700/50 shadow-lg shadow-black/20',
    bordered: 'bg-transparent border border-slate-700/50',
  };

  return (
    <div
      className={cn('rounded-xl', variantClasses[variant], className)}
      {...props}
    >
      {children}
    </div>
  );
}
