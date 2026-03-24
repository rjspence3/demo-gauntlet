import React, { useState, useCallback } from 'react';
import { Upload, Loader2, ArrowRight } from 'lucide-react';
import { DGButton } from './ui';

interface DeckUploadProps {
    onUploadComplete: (file: File) => void;
}

export const DeckUpload: React.FC<DeckUploadProps> = ({ onUploadComplete }) => {
    const [isDragging, setIsDragging] = useState(false);
    const [isUploading, setIsUploading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const handleDragOver = useCallback((e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(true);
    }, []);

    const handleDragLeave = useCallback((e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(false);
    }, []);

    const handleDrop = useCallback((e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(false);
        setError(null);

        const files = e.dataTransfer.files;
        if (files.length > 0) {
            validateAndUpload(files[0]);
        }
    }, []);

    const handleFileSelect = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files.length > 0) {
            validateAndUpload(e.target.files[0]);
        }
    }, []);

    const validateAndUpload = (file: File) => {
        const validTypes = [
            'application/pdf',
            'application/vnd.openxmlformats-officedocument.presentationml.presentation',
            'application/vnd.ms-powerpoint',
        ];

        if (
            !validTypes.includes(file.type) &&
            !file.name.endsWith('.pptx') &&
            !file.name.endsWith('.ppt') &&
            !file.name.endsWith('.pdf')
        ) {
            setError('Please upload a valid PDF or PowerPoint file.');
            return;
        }

        setIsUploading(true);
        onUploadComplete(file);
    };

    return (
        <div className="flex flex-col items-center justify-center min-h-[75vh] w-full max-w-3xl mx-auto px-6">
            {/* Hero — Pitch energy: big, confident, centered */}
            <div className="text-center mb-14">
                <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-ai-50 border border-ai-200 mb-6">
                    <div className="w-1.5 h-1.5 rounded-full bg-ai-500 animate-soft-pulse" />
                    <span className="text-xs font-medium text-ai-600 tracking-wide">AI-Powered Analysis</span>
                </div>
                <h1 className="text-5xl sm:text-6xl font-bold text-text-primary mb-5 tracking-tight leading-[1.05]">
                    Stress-Test Your Demo
                </h1>
                <p className="text-lg sm:text-xl text-text-muted max-w-lg mx-auto leading-relaxed">
                    Upload a sales deck. Face your toughest challenger.
                </p>
            </div>

            {/* Drop zone — glassmorphism card */}
            <div
                className={[
                    'w-full max-w-xl rounded-2xl border-2 border-dashed transition-all duration-200',
                    'flex flex-col items-center justify-center cursor-pointer py-16 px-8',
                    'backdrop-blur-sm',
                    isDragging
                        ? 'border-ai-400 bg-ai-50/60 shadow-ai-glow'
                        : 'border-ai-200 hover:border-ai-300 bg-white/70 hover:bg-white/80',
                    isUploading ? 'pointer-events-none opacity-60' : '',
                ].join(' ')}
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
                onClick={() => !isUploading && document.getElementById('file-upload')?.click()}
            >
                <div className="text-center">
                    <div className={[
                        'w-14 h-14 rounded-2xl flex items-center justify-center mx-auto mb-6 transition-all',
                        isDragging
                            ? 'bg-ai-100 text-ai-500 shadow-ai-glow'
                            : 'bg-ai-50 text-ai-400',
                    ].join(' ')}>
                        {isUploading
                            ? <Loader2 className="w-6 h-6 animate-spin text-ai-500" />
                            : <Upload className="w-6 h-6" />
                        }
                    </div>

                    <p className="text-base font-semibold text-text-primary mb-1.5">
                        {isUploading ? 'Uploading...' : 'Drag & drop your deck here'}
                    </p>
                    <p className="text-text-faint text-sm mb-7">
                        PDF, PPTX, or PPT
                    </p>

                    {!isUploading && (
                        <DGButton variant="primary" size="md" className="pointer-events-none">
                            Browse Files
                            <ArrowRight className="w-3.5 h-3.5 ml-1" />
                        </DGButton>
                    )}

                    <input
                        id="file-upload"
                        type="file"
                        className="hidden"
                        accept=".pdf,.pptx,.ppt"
                        onChange={handleFileSelect}
                    />
                </div>
            </div>

            {error && (
                <div className="mt-5 max-w-xl w-full rounded-xl border border-status-error/20 bg-status-error/5 px-4 py-3">
                    <p className="text-status-error text-sm">{error}</p>
                </div>
            )}
        </div>
    );
};
