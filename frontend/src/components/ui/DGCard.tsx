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
    default: 'bg-[#0A3D6B]/90 backdrop-blur-sm border border-[#0176D3]/25 shadow-glass',
    elevated: 'bg-[#0D4A7F]/90 backdrop-blur-md border border-[#0176D3]/30 shadow-glass-hover',
    bordered: 'bg-transparent border border-[#0176D3]/25',
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
