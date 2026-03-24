import React from 'react';
import { CheckCircle2, Loader2, Circle } from 'lucide-react';

interface ProcessingScreenProps {
    currentStep: ProcessingStep;
}

export type ProcessingStep = 'uploading' | 'extracting' | 'chunking' | 'researching' | 'generating' | 'complete';

const DISPLAY_STEPS: { id: ProcessingStep; label: string; description: string }[] = [
    { id: 'uploading', label: 'Analyzing Deck', description: 'Extracting slides and content' },
    { id: 'extracting', label: 'Processing', description: 'Building semantic index' },
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
        <div className="flex flex-col items-center justify-center min-h-[70vh] max-w-md mx-auto px-6">
            <div className="text-center mb-10">
                <h2 className="text-2xl font-semibold text-text-primary mb-2">
                    Building Your Simulation
                </h2>
                <p className="text-text-muted text-sm">
                    Usually takes about 60–90 seconds
                </p>
            </div>

            <div className="w-full bg-surface border border-border rounded-xl p-6">
                <div className="space-y-4">
                    {DISPLAY_STEPS.map((step, index) => {
                        const status = getStepStatus(index);

                        return (
                            <div key={step.id} className="flex items-center gap-3">
                                <div className="flex-shrink-0 w-7 h-7 flex items-center justify-center">
                                    {status === 'completed' && (
                                        <CheckCircle2 className="w-5 h-5 text-status-success" />
                                    )}
                                    {status === 'active' && (
                                        <Loader2 className="w-5 h-5 text-brand-500 animate-spin" />
                                    )}
                                    {status === 'pending' && (
                                        <Circle className="w-5 h-5 text-text-faint" />
                                    )}
                                </div>

                                <div className="flex-1 min-w-0">
                                    <p className={[
                                        'text-sm font-medium',
                                        status === 'completed' ? 'text-text-muted' : '',
                                        status === 'active' ? 'text-text-primary' : '',
                                        status === 'pending' ? 'text-text-faint' : '',
                                    ].join(' ')}>
                                        {step.label}
                                    </p>
                                    {status === 'active' && (
                                        <p className="text-xs text-text-faint mt-0.5 animate-pulse">
                                            {step.description}
                                        </p>
                                    )}
                                </div>
                            </div>
                        );
                    })}
                </div>

                {/* Progress bar */}
                <div className="mt-6 pt-5 border-t border-border">
                    <div className="flex items-center justify-between mb-2">
                        <span className="text-[10px] text-text-faint font-medium uppercase tracking-wider">Progress</span>
                        <span className="text-[10px] text-text-muted font-mono tabular-nums">
                            {Math.min(currentDisplayIndex, DISPLAY_STEPS.length)}/{DISPLAY_STEPS.length}
                        </span>
                    </div>
                    <div className="w-full bg-surface-overlay rounded-full h-1 overflow-hidden">
                        <div
                            className="bg-brand-500 h-full rounded-full transition-all duration-700 ease-out"
                            style={{ width: `${progressPercent}%` }}
                        />
                    </div>
                </div>
            </div>
        </div>
    );
};
