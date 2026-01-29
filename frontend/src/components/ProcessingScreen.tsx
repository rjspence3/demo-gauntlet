import React, { useEffect, useState } from 'react';

interface ProcessingScreenProps {
    currentStep: ProcessingStep;
}

export type ProcessingStep = 'uploading' | 'extracting' | 'chunking' | 'researching' | 'generating' | 'complete';

export const ProcessingScreen: React.FC<ProcessingScreenProps> = ({ currentStep }) => {
    const steps: { id: ProcessingStep; label: string }[] = [
        { id: 'uploading', label: 'Uploading deck' },
        { id: 'extracting', label: 'Extracting slides' },
        { id: 'chunking', label: 'Chunking and embeddings' },
        { id: 'researching', label: 'Running deep research' },
        { id: 'generating', label: 'Generating challenger questions' },
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

    return (
        <div className="flex flex-col items-center justify-center min-h-[600px] max-w-2xl mx-auto p-6">
            <div className="text-center mb-10">
                <h2 className="text-3xl font-bold text-gray-900 mb-2">
                    Building Your Simulation
                </h2>
                <p className="text-gray-600">
                    We're analyzing your deck and preparing the gauntlet.
                </p>
            </div>

            <div className="w-full bg-white rounded-xl shadow-sm border border-gray-200 p-8">
                <div className="space-y-6">
                    {steps.map((step) => {
                        const status = getStepStatus(step.id);

                        return (
                            <div key={step.id} className="flex items-center group">
                                <div className={`
                  flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center mr-4 transition-colors duration-300
                  ${status === 'completed' ? 'bg-green-100 text-green-600' : ''}
                  ${status === 'active' ? 'bg-blue-100 text-blue-600' : ''}
                  ${status === 'pending' ? 'bg-gray-100 text-gray-400' : ''}
                `}>
                                    {status === 'completed' && (
                                        <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                                        </svg>
                                    )}
                                    {status === 'active' && (
                                        <div className="w-2.5 h-2.5 bg-blue-600 rounded-full animate-pulse" />
                                    )}
                                    {status === 'pending' && (
                                        <div className="w-2.5 h-2.5 bg-gray-400 rounded-full" />
                                    )}
                                </div>

                                <div className="flex-1">
                                    <span className={`
                    text-lg font-medium transition-colors duration-300
                    ${status === 'completed' ? 'text-gray-900' : ''}
                    ${status === 'active' ? 'text-blue-600' : ''}
                    ${status === 'pending' ? 'text-gray-400' : ''}
                  `}>
                                        {step.label}
                                    </span>
                                </div>

                                {status === 'active' && (
                                    <div className="text-sm text-blue-600 animate-pulse font-medium">
                                        Processing...
                                    </div>
                                )}
                            </div>
                        );
                    })}
                </div>

                <div className="mt-8 pt-6 border-t border-gray-100">
                    <div className="w-full bg-gray-100 rounded-full h-2">
                        <div
                            className="bg-blue-600 h-2 rounded-full transition-all duration-500 ease-out"
                            style={{
                                width: currentStep === 'complete' ? '100%' :
                                    `${(steps.findIndex(s => s.id === currentStep) / steps.length) * 100}%`
                            }}
                        />
                    </div>
                </div>
            </div>
        </div>
    );
};
