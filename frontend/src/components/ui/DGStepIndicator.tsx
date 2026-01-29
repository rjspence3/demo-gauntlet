import React from 'react';

export interface DGStepIndicatorProps {
  currentStep: number;
  totalSteps: number;
  label: string;
}

export function DGStepIndicator({
  currentStep,
  totalSteps,
  label,
}: DGStepIndicatorProps) {
  return (
    <div className="inline-flex items-center gap-2 text-sm">
      <span className="px-2.5 py-0.5 rounded-full bg-slate-800 text-slate-400 font-mono text-xs">
        {currentStep} / {totalSteps}
      </span>
      <span className="text-slate-500">{label}</span>
    </div>
  );
}
