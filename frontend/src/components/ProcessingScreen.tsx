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
            <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-[#0176D3]/15 border border-[#0176D3]/30 mb-8">
                <div className="w-1.5 h-1.5 rounded-full bg-[#0176D3] animate-soft-pulse" />
                <span className="text-xs font-medium text-[#3392DF]">Analyzing</span>
            </div>

            <div className="text-center mb-10">
                <h2 className="text-2xl font-bold text-white mb-2 tracking-tight">
                    Building Your Simulation
                </h2>
                <p className="text-white/60 text-sm">
                    Usually 60–90 seconds
                </p>
            </div>

            {/* Timeline card — dark navy surface */}
            <div className="w-full bg-[#0A3D6B]/90 backdrop-blur-sm border border-[#0176D3]/25 rounded-2xl shadow-glass p-6">
                <div className="space-y-5">
                    {DISPLAY_STEPS.map((step, index) => {
                        const status = getStepStatus(index);

                        return (
                            <div key={step.id} className="flex items-start gap-4">
                                {/* Step indicator */}
                                <div className="flex flex-col items-center">
                                    <div className="flex-shrink-0 w-8 h-8 flex items-center justify-center">
                                        {status === 'completed' && (
                                            <CheckCircle2 className="w-5 h-5 text-[#2E844A]" />
                                        )}
                                        {status === 'active' && (
                                            <div className="relative">
                                                <Loader2 className="w-5 h-5 text-[#0176D3] animate-spin" />
                                            </div>
                                        )}
                                        {status === 'pending' && (
                                            <Circle className="w-5 h-5 text-white/20" />
                                        )}
                                    </div>
                                    {index < DISPLAY_STEPS.length - 1 && (
                                        <div className={[
                                            'w-px h-6 mt-1',
                                            status === 'completed' ? 'bg-[#2E844A]/30' : 'bg-white/12',
                                        ].join(' ')} />
                                    )}
                                </div>

                                {/* Step content */}
                                <div className="flex-1 min-w-0 pt-1">
                                    <p className={[
                                        'text-sm font-semibold',
                                        status === 'completed' ? 'text-white/60' : '',
                                        status === 'active' ? 'text-[#0176D3]' : '',
                                        status === 'pending' ? 'text-white/30' : '',
                                    ].join(' ')}>
                                        {step.label}
                                    </p>
                                    {status === 'active' && (
                                        <p className="text-xs text-white/60 mt-0.5 animate-soft-pulse">
                                            {step.description}
                                        </p>
                                    )}
                                    {status === 'completed' && (
                                        <p className="text-xs text-white/40 mt-0.5">
                                            Complete
                                        </p>
                                    )}
                                </div>
                            </div>
                        );
                    })}
                </div>

                {/* Progress bar — SF blue */}
                <div className="mt-6 pt-5 border-t border-white/12">
                    <div className="flex items-center justify-between mb-2">
                        <span className="text-[10px] text-white/40 font-medium uppercase tracking-wider">Progress</span>
                        <span className="text-[10px] text-white/60 font-mono tabular-nums">
                            {Math.min(currentDisplayIndex, DISPLAY_STEPS.length)}/{DISPLAY_STEPS.length}
                        </span>
                    </div>
                    <div className="w-full bg-white/10 rounded-full h-1.5 overflow-hidden">
                        <div
                            className="bg-gradient-to-r from-[#0176D3] to-[#3392DF] h-full rounded-full transition-all duration-700 ease-out"
                            style={{ width: `${progressPercent}%` }}
                        />
                    </div>
                </div>
            </div>
        </div>
    );
};
