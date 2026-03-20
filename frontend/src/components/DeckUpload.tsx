import React, { useState, useCallback } from 'react';
import { Upload } from 'lucide-react';
import { DGCard, DGButton } from './ui';

interface DeckUploadProps {
    onUploadComplete: (file: File) => void;
}

export const DeckUpload: React.FC<DeckUploadProps> = ({ onUploadComplete }) => {
    const [isDragging, setIsDragging] = useState(false);
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

        onUploadComplete(file);
    };

    return (
        <div className="flex flex-col items-center justify-center min-h-[600px] w-full max-w-4xl mx-auto p-6">
            {/* Hero heading */}
            <div className="text-center mb-10 sm:mb-12">
                <h1 className="text-4xl sm:text-5xl font-bold text-white mb-4 tracking-tight leading-tight">
                    Ready to run the gauntlet?
                </h1>
                <p className="text-lg sm:text-xl text-slate-400 max-w-xl mx-auto leading-relaxed">
                    Upload your deck and benchmark your demo readiness against AI-powered challengers.
                </p>
            </div>

            {/* Drop zone */}
            <div
                className={[
                    'w-full max-w-2xl rounded-2xl border-2 border-dashed transition-all duration-300 ease-in-out',
                    'flex flex-col items-center justify-center cursor-pointer py-16 px-8',
                    isDragging
                        ? 'border-cyan-400 bg-cyan-400/5 scale-[1.02]'
                        : 'border-slate-700 hover:border-slate-500 bg-slate-900/40 hover:bg-slate-900/60',
                ].join(' ')}
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
                onClick={() => document.getElementById('file-upload')?.click()}
            >
                <div className="text-center">
                    <div className={[
                        'w-16 h-16 rounded-2xl flex items-center justify-center mx-auto mb-6 transition-colors',
                        isDragging ? 'bg-cyan-400/20 text-cyan-400' : 'bg-slate-800 text-slate-400',
                    ].join(' ')}>
                        <Upload className="w-8 h-8" />
                    </div>

                    <h3 className="text-lg font-semibold text-white mb-2">
                        Drag & drop your deck here
                    </h3>
                    <p className="text-slate-500 mb-8 text-sm">
                        Supports PDF, PPTX, or PPT
                    </p>

                    <DGButton variant="primary" size="md" className="pointer-events-none">
                        Select File
                    </DGButton>

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
                <DGCard variant="elevated" className="mt-6 max-w-2xl w-full border-rose-500/40 bg-rose-500/10 p-4">
                    <div className="flex items-center gap-3 text-rose-300 text-sm">
                        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" className="w-5 h-5 flex-shrink-0">
                            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.28 7.22a.75.75 0 00-1.06 1.06L8.94 10l-1.72 1.72a.75.75 0 101.06 1.06L10 11.06l1.72 1.72a.75.75 0 101.06-1.06L11.06 10l1.72-1.72a.75.75 0 00-1.06-1.06L10 8.94 8.28 7.22z" clipRule="evenodd" />
                        </svg>
                        {error}
                    </div>
                </DGCard>
            )}
        </div>
    );
};
