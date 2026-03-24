import React from 'react';
import { cn } from '../../lib/utils';
import { X } from 'lucide-react';
import { DGIconButton } from './DGIconButton';

export interface DGModalProps {
  isOpen: boolean;
  onClose: () => void;
  title?: string;
  description?: string;
  size?: 'sm' | 'md' | 'lg' | 'xl';
  children: React.ReactNode;
}

export function DGModal({
  isOpen,
  onClose,
  title,
  description,
  size = 'lg',
  children,
}: DGModalProps) {
  if (!isOpen) return null;

  const sizeClasses = {
    sm: 'w-[95vw] sm:w-full sm:max-w-md',
    md: 'w-[95vw] sm:w-full sm:max-w-lg',
    lg: 'w-[95vw] sm:w-full sm:max-w-2xl',
    xl: 'w-[95vw] sm:w-full sm:max-w-4xl',
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 animate-fade-in">
      <div
        className="absolute inset-0 bg-black/40 backdrop-blur-sm"
        onClick={onClose}
      />
      <div
        className={cn(
          'relative z-10 flex flex-col max-h-[90vh] bg-white/95 backdrop-blur-md border border-border-ai rounded-2xl shadow-glass-hover',
          sizeClasses[size]
        )}
      >
        {title && (
          <div className="flex items-center justify-between p-5 border-b border-border">
            <div>
              <h3 className="text-lg font-semibold text-text-primary">
                {title}
              </h3>
              {description && (
                <p className="text-sm text-text-muted mt-1">{description}</p>
              )}
            </div>
            <DGIconButton
              icon={<X className="w-4 h-4" />}
              ariaLabel="Close modal"
              onClick={onClose}
              size="sm"
            />
          </div>
        )}

        {title ? (
          <div className="flex-1 overflow-y-auto p-5">{children}</div>
        ) : (
          <div className="flex-1 overflow-hidden flex flex-col">{children}</div>
        )}
      </div>
    </div>
  );
}
