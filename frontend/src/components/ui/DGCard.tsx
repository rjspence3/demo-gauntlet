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
    default: 'bg-white/85 backdrop-blur-sm border border-border-ai shadow-glass',
    elevated: 'bg-white/90 backdrop-blur-md border border-border-ai shadow-glass-hover',
    bordered: 'bg-transparent border border-border-ai',
  };

  return (
    <div
      className={cn('rounded-2xl', variantClasses[variant], className)}
      {...props}
    >
      {children}
    </div>
  );
}
