import React from 'react';
import { cn } from '../../lib/utils';
import { X } from 'lucide-react';
import { DGCard } from './DGCard';
import { DGIconButton } from './DGIconButton';

export interface DGModalProps {
  isOpen: boolean;
  onClose: () => void;
  /** When provided, DGModal renders its own header with title and close button */
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
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/80 backdrop-blur-sm"
        onClick={onClose}
      />

      {/* Content */}
      <DGCard
        variant="elevated"
        className={cn(
          'relative z-10 flex flex-col max-h-[90vh]',
          sizeClasses[size]
        )}
      >
        {/* Header - only rendered when title is provided */}
        {title && (
          <div className="flex items-center justify-between p-6 border-b border-slate-700/50">
            <div>
              <h3 className="text-xl font-semibold text-white">
                {title}
              </h3>
              {description && (
                <p className="text-sm text-slate-400 mt-1">{description}</p>
              )}
            </div>
            <DGIconButton
              icon={<X className="w-5 h-5" />}
              ariaLabel="Close modal"
              onClick={onClose}
              size="sm"
            />
          </div>
        )}

        {/* Body - when title is provided, add padding; otherwise children control layout */}
        {title ? (
          <div className="flex-1 overflow-y-auto p-6">{children}</div>
        ) : (
          <div className="flex-1 overflow-hidden flex flex-col">{children}</div>
        )}
      </DGCard>
    </div>
  );
}
