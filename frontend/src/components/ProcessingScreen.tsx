import React from 'react';
import { CheckCircle2, Loader2, Circle } from 'lucide-react';
import { DGCard } from './ui';

interface ProcessingScreenProps {
    currentStep: ProcessingStep;
}

export type ProcessingStep = 'uploading' | 'extracting' | 'chunking' | 'researching' | 'generating' | 'complete';

// Map internal step IDs to the 3 honest user-facing steps
const DISPLAY_STEPS: { id: ProcessingStep; label: string; description: string }[] = [
    { id: 'uploading', label: 'Uploading', description: 'Sending your deck to the server' },
    { id: 'extracting', label: 'Processing', description: 'Extracting slides and building index' },
    { id: 'researching', label: 'Researching', description: 'Gathering competitive intelligence' },
];

const STEP_TO_DISPLAY: Record<ProcessingStep, number> = {
    uploading: 0,
    extracting: 1,
    chunking: 1,
    researching: 2,
    generating: 2,
    complete: 3,
};

export const ProcessingScreen: React.FC<ProcessingScreenProps> = ({ currentStep }) => {
    const currentDisplayIndex = STEP_TO_DISPLAY[currentStep];

    const getStepStatus = (index: number) => {
        if (currentStep === 'complete') return 'completed';
        if (index < currentDisplayIndex) return 'completed';
        if (index === currentDisplayIndex) return 'active';
        return 'pending';
    };

    const progressPercent = currentStep === 'complete'
        ? 100
        : (currentDisplayIndex / DISPLAY_STEPS.length) * 100;

    return (
        <div className="flex flex-col items-center justify-center min-h-[600px] max-w-2xl mx-auto p-6">
            <div className="text-center mb-10">
                <h2 className="text-3xl font-bold text-slate-900 mb-2">
                    Building Your Simulation
                </h2>
                <p className="text-slate-600">
                    Analyzing your deck and preparing the gauntlet.
                </p>
            </div>

            <DGCard variant="elevated" className="w-full p-8">
                <div className="space-y-5">
                    {DISPLAY_STEPS.map((step, index) => {
                        const status = getStepStatus(index);

                        return (
                            <div key={step.id} className="flex items-center gap-4">
                                {/* Status icon */}
                                <div className="flex-shrink-0 w-9 h-9 flex items-center justify-center">
                                    {status === 'completed' && (
                                        <CheckCircle2 className="w-7 h-7 text-emerald-500" />
                                    )}
                                    {status === 'active' && (
                                        <Loader2 className="w-7 h-7 text-orange-500 animate-spin" />
                                    )}
                                    {status === 'pending' && (
                                        <Circle className="w-7 h-7 text-slate-300" />
                                    )}
                                </div>

                                {/* Label */}
                                <div className="flex-1 min-w-0">
                                    <p className={[
                                        'text-sm font-medium leading-tight',
                                        status === 'completed' ? 'text-slate-600' : '',
                                        status === 'active' ? 'text-slate-900' : '',
                                        status === 'pending' ? 'text-slate-400' : '',
                                    ].join(' ')}>
                                        {step.label}
                                    </p>
                                    {status === 'active' && (
                                        <p className="text-xs text-slate-500 mt-0.5 animate-pulse">
                                            {step.description}
                                        </p>
                                    )}
                                </div>

                                {status === 'active' && (
                                    <span className="text-xs text-orange-500 font-mono font-medium flex-shrink-0">
                                        Processing...
                                    </span>
                                )}
                            </div>
                        );
                    })}
                </div>

                {/* Progress bar */}
                <div className="mt-8 pt-6 border-t border-slate-100">
                    <div className="flex items-center justify-between mb-2">
                        <span className="text-xs text-slate-400 font-mono uppercase tracking-wider">Progress</span>
                        <span className="text-xs text-slate-500 font-mono tabular-nums">
                            {Math.min(currentDisplayIndex, DISPLAY_STEPS.length)}/{DISPLAY_STEPS.length}
                        </span>
                    </div>
                    <div className="w-full bg-slate-100 rounded-full h-1.5 overflow-hidden">
                        <div
                            className="bg-orange-500 h-full rounded-full transition-all duration-700 ease-out"
                            style={{ width: `${progressPercent}%` }}
                        />
                    </div>
                </div>
            </DGCard>
        </div>
    );
};
