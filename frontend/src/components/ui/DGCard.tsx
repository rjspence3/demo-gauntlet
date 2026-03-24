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
    default: 'bg-white border border-gray-200 shadow-sm',
    elevated: 'bg-gray-50 border border-gray-200 shadow-sm',
    bordered: 'bg-transparent border border-gray-200',
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
