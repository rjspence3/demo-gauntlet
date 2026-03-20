import React from 'react';
import { CheckCircle2, Loader2, Circle } from 'lucide-react';
import { DGCard } from './ui';

interface ProcessingScreenProps {
    currentStep: ProcessingStep;
}

export type ProcessingStep = 'uploading' | 'extracting' | 'chunking' | 'researching' | 'generating' | 'complete';

export const ProcessingScreen: React.FC<ProcessingScreenProps> = ({ currentStep }) => {
    const steps: { id: ProcessingStep; label: string; description: string }[] = [
        { id: 'uploading', label: 'Uploading deck', description: 'Sending your file to the server' },
        { id: 'extracting', label: 'Extracting slides', description: 'Parsing slide content and structure' },
        { id: 'chunking', label: 'Building embeddings', description: 'Indexing content for semantic search' },
        { id: 'researching', label: 'Running deep research', description: 'Gathering competitive intelligence' },
        { id: 'generating', label: 'Generating questions', description: 'Crafting challenger-specific objections' },
    ];

    const getStepStatus = (stepId: ProcessingStep) => {
        const stepOrder = steps.map(s => s.id);
        const currentIndex = stepOrder.indexOf(currentStep);
        const stepIndex = stepOrder.indexOf(stepId);

        if (currentStep === 'complete') return 'completed';
        if (stepIndex < currentIndex) return 'completed';
        if (stepIndex === currentIndex) return 'active';
        return 'pending';
    };

    const completedCount = currentStep === 'complete'
        ? steps.length
        : steps.findIndex(s => s.id === currentStep);
    const progressPercent = (completedCount / steps.length) * 100;

    return (
        <div className="flex flex-col items-center justify-center min-h-[600px] max-w-2xl mx-auto p-6">
            <div className="text-center mb-10">
                <h2 className="text-3xl font-bold text-white mb-2">
                    Building Your Simulation
                </h2>
                <p className="text-slate-400">
                    Analyzing your deck and preparing the gauntlet.
                </p>
            </div>

            <DGCard className="w-full p-8">
                <div className="space-y-5">
                    {steps.map((step) => {
                        const status = getStepStatus(step.id);

                        return (
                            <div key={step.id} className="flex items-center gap-4">
                                {/* Status icon */}
                                <div className="flex-shrink-0 w-9 h-9 flex items-center justify-center">
                                    {status === 'completed' && (
                                        <CheckCircle2 className="w-7 h-7 text-emerald-400" />
                                    )}
                                    {status === 'active' && (
                                        <Loader2 className="w-7 h-7 text-cyan-400 animate-spin" />
                                    )}
                                    {status === 'pending' && (
                                        <Circle className="w-7 h-7 text-slate-700" />
                                    )}
                                </div>

                                {/* Label */}
                                <div className="flex-1 min-w-0">
                                    <p className={[
                                        'text-sm font-medium leading-tight',
                                        status === 'completed' ? 'text-slate-300' : '',
                                        status === 'active' ? 'text-white' : '',
                                        status === 'pending' ? 'text-slate-600' : '',
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
                                    <span className="text-xs text-cyan-400 font-mono font-medium flex-shrink-0">
                                        Processing...
                                    </span>
                                )}
                            </div>
                        );
                    })}
                </div>

                {/* Progress bar */}
                <div className="mt-8 pt-6 border-t border-slate-800">
                    <div className="flex items-center justify-between mb-2">
                        <span className="text-xs text-slate-500 font-mono uppercase tracking-wider">Progress</span>
                        <span className="text-xs text-slate-400 font-mono tabular-nums">
                            {completedCount}/{steps.length}
                        </span>
                    </div>
                    <div className="w-full bg-slate-800 rounded-full h-1.5 overflow-hidden">
                        <div
                            className="bg-gradient-to-r from-cyan-400 to-cyan-300 h-full rounded-full transition-all duration-700 ease-out"
                            style={{ width: `${progressPercent}%` }}
                        />
                    </div>
                </div>
            </DGCard>
        </div>
    );
};
