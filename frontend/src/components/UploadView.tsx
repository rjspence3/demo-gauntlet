import React, { useCallback, useState, useEffect } from 'react';
import { UploadCloud, FileText, Loader2, AlertCircle, Sparkles, CheckCircle2, Circle } from 'lucide-react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';
import { uploadDeck, UploadResponse } from '../api/client';

interface UploadViewProps {
    onUploadComplete: (sessionId: string) => void;
}

const PROCESSING_STEPS = [
    "Extracting slides from deck...",
    "Chunking content & generating embeddings...",
    "Running deep research agent...",
    "Generating challenger questions...",
    "Finalizing simulation environment..."
];

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
        }, 3000); // Advance every 3 seconds (simulated)

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
            // Ensure we show the last step before completing
            setCurrentStep(PROCESSING_STEPS.length - 1);
            setTimeout(() => {
                onUploadComplete(response.session_id);
            }, 1000);
        } catch (err) {
            console.error(err);
            setError('Failed to upload deck. Please try again.');
            setIsUploading(false);
        }
    };

    return (
        <div className="flex flex-col items-center justify-center min-h-[70vh] w-full max-w-3xl mx-auto p-6 animate-fade-in">
            <div className="text-center mb-12 relative">
                <div className="absolute -top-10 left-1/2 transform -translate-x-1/2 w-32 h-32 bg-neon-blue/20 rounded-full blur-3xl"></div>
                <h1 className="text-6xl font-display font-bold mb-6 relative z-10">
                    <span className="bg-gradient-to-r from-white via-blue-100 to-gray-400 bg-clip-text text-transparent">
                        Demo Gauntlet
                    </span>
                </h1>
                <p className="text-gray-400 text-xl max-w-lg mx-auto font-light leading-relaxed">
                    Upload your pitch deck. <span className="text-neon-blue font-medium">Survive the AI inquisition.</span>
                </p>
            </div>

            <div
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
                className={twMerge(
                    "w-full glass-panel rounded-3xl p-16 transition-all duration-500 flex flex-col items-center justify-center cursor-pointer group relative overflow-hidden min-h-[400px]",
                    isDragging
                        ? "border-neon-blue bg-neon-blue/5 scale-[1.02] shadow-[0_0_30px_rgba(0,243,255,0.15)]"
                        : "hover:border-neon-blue/50 hover:bg-white/5",
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
                        <div className="flex items-center mb-8 w-full justify-center">
                            <div className="relative">
                                <div className="absolute inset-0 bg-neon-blue blur-xl opacity-20 animate-pulse"></div>
                                <Loader2 className="w-12 h-12 text-neon-blue animate-spin relative z-10" />
                            </div>
                            <h3 className="text-2xl font-bold text-white ml-4 font-display">Building Simulation...</h3>
                        </div>

                        <div className="w-full space-y-4">
                            {PROCESSING_STEPS.map((step, index) => {
                                const isCompleted = index < currentStep;
                                const isCurrent = index === currentStep;
                                const isPending = index > currentStep;

                                return (
                                    <div key={index} className={twMerge(
                                        "flex items-center transition-all duration-500",
                                        isPending ? "opacity-30" : "opacity-100"
                                    )}>
                                        <div className="mr-4">
                                            {isCompleted ? (
                                                <CheckCircle2 className="w-6 h-6 text-neon-green" />
                                            ) : isCurrent ? (
                                                <div className="w-6 h-6 rounded-full border-2 border-neon-blue border-t-transparent animate-spin" />
                                            ) : (
                                                <Circle className="w-6 h-6 text-gray-600" />
                                            )}
                                        </div>
                                        <span className={twMerge(
                                            "font-mono text-sm",
                                            isCurrent ? "text-neon-blue font-bold" : "text-gray-300"
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
                        <div className="p-6 rounded-2xl bg-white/5 border border-white/10 group-hover:border-neon-blue/30 group-hover:bg-neon-blue/10 transition-all duration-300 mb-8 relative">
                            <div className="absolute inset-0 bg-neon-blue/20 blur-xl opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
                            <UploadCloud className="w-16 h-16 text-gray-300 group-hover:text-neon-blue transition-colors relative z-10" />
                        </div>
                        <p className="text-2xl font-bold text-white mb-3 group-hover:text-neon-blue transition-colors font-display">
                            Drag & drop your deck
                        </p>
                        <p className="text-gray-500 group-hover:text-gray-400 transition-colors">
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
            </div>

            {error && (
                <div className="mt-8 p-4 bg-danger-red/10 border border-danger-red/20 rounded-xl flex items-center text-danger-red animate-slide-up backdrop-blur-sm">
                    <AlertCircle className="w-5 h-5 mr-3" />
                    <span className="font-medium">{error}</span>
                </div>
            )}

            <div className="mt-12 flex items-center space-x-8 text-sm text-gray-500 font-mono">
                <div className="flex items-center">
                    <Sparkles className="w-4 h-4 mr-2 text-neon-purple" />
                    <span>AI Analysis</span>
                </div>
                <div className="flex items-center">
                    <FileText className="w-4 h-4 mr-2 text-neon-blue" />
                    <span>Smart Parsing</span>
                </div>
            </div>
        </div>
    );
};
