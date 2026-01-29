import React, { useCallback, useState, useEffect } from 'react';
import { UploadCloud, FileText, Loader2, AlertCircle, Sparkles, CheckCircle2, Circle } from 'lucide-react';
import { cn } from '../lib/utils';
import { uploadDeck, getSessionStatus } from '../api/client';
import { DGCard, DGStepIndicator } from './ui';

/**
 * Props for the UploadView component.
 */
interface UploadViewProps {
    /** Callback when upload is complete with the new session ID. */
    onUploadComplete: (sessionId: string) => void;
}

const PROCESSING_STEPS = [
    "Extracting slides from deck...",
    "Chunking content & generating embeddings...",
    "Running deep research agent...",
    "Generating challenger questions...",
    "Finalizing simulation environment..."
];

/**
 * Component for handling deck uploads and showing processing progress.
 */
export const UploadView: React.FC<UploadViewProps> = ({ onUploadComplete }) => {
    const [isDragging, setIsDragging] = useState(false);
    const [isUploading, setIsUploading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [currentStep, setCurrentStep] = useState(0);

    const handleDragOver = useCallback((e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(true);
    }, []);

    const handleDragLeave = useCallback((e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(false);
    }, []);

    const handleDrop = useCallback(async (e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(false);
        setError(null);

        const files = e.dataTransfer.files;
        if (files.length === 0) return;

        const file = files[0];
        await processFile(file);
    }, []);

    const handleFileSelect = useCallback(async (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files.length > 0) {
            setError(null);
            await processFile(e.target.files[0]);
        }
    }, []);

    // Simulate progress steps
    useEffect(() => {
        if (!isUploading) {
            setCurrentStep(0);
            return;
        }

        const interval = setInterval(() => {
            setCurrentStep(prev => {
                if (prev < PROCESSING_STEPS.length - 1) {
                    return prev + 1;
                }
                return prev;
            });
        }, 3000);

        return () => clearInterval(interval);
    }, [isUploading]);

    const processFile = async (file: File) => {
        if (!file.name.endsWith('.pdf') && !file.name.endsWith('.pptx')) {
            setError('Only PDF and PPTX files are supported.');
            return;
        }

        setIsUploading(true);
        try {
            const response = await uploadDeck(file);
            const sessionId = response.session_id;

            // Poll for status
            const pollInterval = setInterval(async () => {
                try {
                    const statusRes = await getSessionStatus(sessionId);
                    if (statusRes.status === 'completed') {
                        clearInterval(pollInterval);
                        setCurrentStep(PROCESSING_STEPS.length - 1);
                        setTimeout(() => {
                            onUploadComplete(sessionId);
                        }, 1000);
                    } else if (statusRes.status === 'failed') {
                        clearInterval(pollInterval);
                        setError('Processing failed. Please try again.');
                        setIsUploading(false);
                    }
                } catch (err) {
                    console.error("Polling error", err);
                }
            }, 2000);

        } catch (err) {
            console.error(err);
            setError('Failed to upload deck. Please try again.');
            setIsUploading(false);
        }
    };

    return (
        <div className="flex flex-col items-center justify-center min-h-[70vh] w-full max-w-3xl mx-auto p-4 sm:p-6 animate-fade-in">
            <div className="text-center mb-8 sm:mb-12 relative">
                <DGStepIndicator currentStep={1} totalSteps={5} label="Upload Deck" />
                <div className="absolute -top-10 left-1/2 transform -translate-x-1/2 w-24 sm:w-32 h-24 sm:h-32 bg-cyan-400/20 rounded-full blur-3xl"></div>
                <h1 className="text-4xl sm:text-6xl font-bold mb-4 sm:mb-6 relative z-10 mt-4">
                    <span className="bg-gradient-to-r from-white via-blue-100 to-slate-400 bg-clip-text text-transparent">
                        Demo Gauntlet
                    </span>
                </h1>
                <p className="text-slate-400 text-lg sm:text-xl max-w-lg mx-auto font-light leading-relaxed px-4">
                    Upload your pitch deck. <span className="text-cyan-400 font-medium">Survive the AI inquisition.</span>
                </p>
            </div>

            <DGCard
                variant="bordered"
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
                className={cn(
                    "w-full p-8 sm:p-16 transition-all duration-500 flex flex-col items-center justify-center cursor-pointer group relative overflow-hidden min-h-[300px] sm:min-h-[400px]",
                    isDragging && "border-cyan-400 bg-cyan-400/5 scale-[1.02] shadow-[0_0_30px_rgba(34,211,238,0.15)]",
                    !isDragging && !isUploading && "hover:border-cyan-400/50 hover:bg-slate-800/50",
                    isUploading && "pointer-events-none cursor-default"
                )}
            >
                <input
                    type="file"
                    id="file-upload"
                    className="hidden"
                    accept=".pdf,.pptx"
                    onChange={handleFileSelect}
                />

                {isUploading ? (
                    <div className="flex flex-col items-start w-full max-w-md z-10">
                        <div className="flex items-center mb-6 sm:mb-8 w-full justify-center">
                            <div className="relative">
                                <div className="absolute inset-0 bg-cyan-400 blur-xl opacity-20 animate-pulse"></div>
                                <Loader2 className="w-10 sm:w-12 h-10 sm:h-12 text-cyan-400 animate-spin relative z-10" />
                            </div>
                            <h3 className="text-xl sm:text-2xl font-bold text-white ml-3 sm:ml-4">Building Simulation...</h3>
                        </div>

                        <div className="w-full space-y-3 sm:space-y-4">
                            {PROCESSING_STEPS.map((step, index) => {
                                const isCompleted = index < currentStep;
                                const isCurrent = index === currentStep;
                                const isPending = index > currentStep;

                                return (
                                    <div key={index} className={cn(
                                        "flex items-center transition-all duration-500",
                                        isPending ? "opacity-30" : "opacity-100"
                                    )}>
                                        <div className="mr-3 sm:mr-4 flex-shrink-0">
                                            {isCompleted ? (
                                                <CheckCircle2 className="w-5 sm:w-6 h-5 sm:h-6 text-emerald-400" />
                                            ) : isCurrent ? (
                                                <div className="w-5 sm:w-6 h-5 sm:h-6 rounded-full border-2 border-cyan-400 border-t-transparent animate-spin" />
                                            ) : (
                                                <Circle className="w-5 sm:w-6 h-5 sm:h-6 text-slate-600" />
                                            )}
                                        </div>
                                        <span className={cn(
                                            "font-mono text-xs sm:text-sm",
                                            isCurrent ? "text-cyan-400 font-bold" : "text-slate-300"
                                        )}>
                                            {step}
                                        </span>
                                    </div>
                                );
                            })}
                        </div>
                    </div>
                ) : (
                    <label htmlFor="file-upload" className="flex flex-col items-center cursor-pointer w-full h-full z-10">
                        <div className="p-4 sm:p-6 rounded-xl bg-slate-800/50 border border-slate-700 group-hover:border-cyan-400/30 group-hover:bg-cyan-400/10 transition-all duration-300 mb-6 sm:mb-8 relative">
                            <div className="absolute inset-0 bg-cyan-400/20 blur-xl opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
                            <UploadCloud className="w-12 sm:w-16 h-12 sm:h-16 text-slate-300 group-hover:text-cyan-400 transition-colors relative z-10" />
                        </div>
                        <p className="text-xl sm:text-2xl font-bold text-white mb-2 sm:mb-3 group-hover:text-cyan-400 transition-colors text-center">
                            Drag & drop your deck
                        </p>
                        <p className="text-slate-500 group-hover:text-slate-400 transition-colors text-sm sm:text-base">
                            Supports PDF and PPTX
                        </p>
                    </label>
                )}

                {/* Decorative Grid */}
                <div className="absolute inset-0 opacity-[0.03] pointer-events-none"
                    style={{
                        backgroundImage: 'linear-gradient(#fff 1px, transparent 1px), linear-gradient(90deg, #fff 1px, transparent 1px)',
                        backgroundSize: '20px 20px'
                    }}>
                </div>
            </DGCard>

            {error && (
                <DGCard className="mt-6 sm:mt-8 p-3 sm:p-4 bg-rose-500/10 border-rose-500/20 animate-slide-up">
                    <div className="flex items-center text-rose-400">
                        <AlertCircle className="w-4 sm:w-5 h-4 sm:h-5 mr-2 sm:mr-3 flex-shrink-0" />
                        <span className="font-medium text-sm sm:text-base">{error}</span>
                    </div>
                </DGCard>
            )}

            <div className="mt-8 sm:mt-12 flex items-center space-x-6 sm:space-x-8 text-xs sm:text-sm text-slate-500 font-mono">
                <div className="flex items-center">
                    <Sparkles className="w-4 h-4 mr-2 text-violet-400" />
                    <span>AI Analysis</span>
                </div>
                <div className="flex items-center">
                    <FileText className="w-4 h-4 mr-2 text-cyan-400" />
                    <span>Smart Parsing</span>
                </div>
            </div>
        </div>
    );
};
