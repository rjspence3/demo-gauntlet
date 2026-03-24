import React from 'react';
import { CheckCircle2, Loader2, Circle } from 'lucide-react';

interface ProcessingScreenProps {
    currentStep: ProcessingStep;
}

export type ProcessingStep = 'uploading' | 'extracting' | 'chunking' | 'researching' | 'generating' | 'complete';

const DISPLAY_STEPS: { id: ProcessingStep; label: string; description: string }[] = [
    { id: 'uploading', label: 'Analyzing deck', description: 'Extracting slides and content' },
    { id: 'extracting', label: 'Researching company', description: 'Gathering competitive intelligence' },
    { id: 'researching', label: 'Building challengers', description: 'Generating persona-based challenges' },
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
        <div className="flex flex-col items-center justify-center min-h-[75vh] max-w-md mx-auto px-6">
            {/* Header badge */}
            <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-ai-50 border border-ai-200 mb-8">
                <div className="w-1.5 h-1.5 rounded-full bg-ai-500 animate-soft-pulse" />
                <span className="text-xs font-medium text-ai-600">Analyzing</span>
            </div>

            <div className="text-center mb-10">
                <h2 className="text-2xl font-bold text-text-primary mb-2 tracking-tight">
                    Building Your Simulation
                </h2>
                <p className="text-text-muted text-sm">
                    Usually 60–90 seconds
                </p>
            </div>

            {/* Timeline card — glassmorphism */}
            <div className="w-full bg-white/85 backdrop-blur-sm border border-border-ai rounded-2xl shadow-glass p-6">
                <div className="space-y-5">
                    {DISPLAY_STEPS.map((step, index) => {
                        const status = getStepStatus(index);

                        return (
                            <div key={step.id} className="flex items-start gap-4">
                                {/* Step indicator */}
                                <div className="flex flex-col items-center">
                                    <div className="flex-shrink-0 w-8 h-8 flex items-center justify-center">
                                        {status === 'completed' && (
                                            <CheckCircle2 className="w-5 h-5 text-status-success" />
                                        )}
                                        {status === 'active' && (
                                            <div className="relative">
                                                <Loader2 className="w-5 h-5 text-ai-500 animate-spin" />
                                            </div>
                                        )}
                                        {status === 'pending' && (
                                            <Circle className="w-5 h-5 text-text-faint/50" />
                                        )}
                                    </div>
                                    {index < DISPLAY_STEPS.length - 1 && (
                                        <div className={[
                                            'w-px h-6 mt-1',
                                            status === 'completed' ? 'bg-status-success/30' : 'bg-border',
                                        ].join(' ')} />
                                    )}
                                </div>

                                {/* Step content */}
                                <div className="flex-1 min-w-0 pt-1">
                                    <p className={[
                                        'text-sm font-semibold',
                                        status === 'completed' ? 'text-text-muted' : '',
                                        status === 'active' ? 'text-ai-600' : '',
                                        status === 'pending' ? 'text-text-faint' : '',
                                    ].join(' ')}>
                                        {step.label}
                                    </p>
                                    {status === 'active' && (
                                        <p className="text-xs text-text-muted mt-0.5 animate-soft-pulse">
                                            {step.description}
                                        </p>
                                    )}
                                    {status === 'completed' && (
                                        <p className="text-xs text-text-faint mt-0.5">
                                            Complete
                                        </p>
                                    )}
                                </div>
                            </div>
                        );
                    })}
                </div>

                {/* Progress bar — indigo accent */}
                <div className="mt-6 pt-5 border-t border-border">
                    <div className="flex items-center justify-between mb-2">
                        <span className="text-[10px] text-text-faint font-medium uppercase tracking-wider">Progress</span>
                        <span className="text-[10px] text-text-muted font-mono tabular-nums">
                            {Math.min(currentDisplayIndex, DISPLAY_STEPS.length)}/{DISPLAY_STEPS.length}
                        </span>
                    </div>
                    <div className="w-full bg-ai-50 rounded-full h-1.5 overflow-hidden">
                        <div
                            className="bg-gradient-to-r from-ai-500 to-ai-400 h-full rounded-full transition-all duration-700 ease-out"
                            style={{ width: `${progressPercent}%` }}
                        />
                    </div>
                </div>
            </div>
        </div>
    );
};
