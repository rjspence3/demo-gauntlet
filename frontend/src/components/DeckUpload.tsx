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
        <div className="flex flex-col items-center justify-center min-h-[70vh] w-full max-w-3xl mx-auto px-6">
            {/* Hero */}
            <div className="text-center mb-12">
                <p className="text-xs font-medium text-brand-500 uppercase tracking-widest mb-4">
                    Sales Deck Analyzer
                </p>
                <h1 className="text-4xl sm:text-5xl font-semibold text-text-primary mb-4 tracking-tight leading-[1.1]">
                    Stress-Test Your Demo
                </h1>
                <p className="text-base sm:text-lg text-text-muted max-w-lg mx-auto leading-relaxed">
                    Upload a sales deck. Face your toughest challenger.
                </p>
            </div>

            {/* Drop zone */}
            <div
                className={[
                    'w-full max-w-xl rounded-xl border border-dashed transition-all duration-200',
                    'flex flex-col items-center justify-center cursor-pointer py-14 px-8',
                    isDragging
                        ? 'border-brand-500 bg-brand-500/5'
                        : 'border-border-hover hover:border-brand-500/50 bg-surface',
                    isUploading ? 'pointer-events-none opacity-60' : '',
                ].join(' ')}
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
                onClick={() => !isUploading && document.getElementById('file-upload')?.click()}
            >
                <div className="text-center">
                    <div className={[
                        'w-12 h-12 rounded-lg flex items-center justify-center mx-auto mb-5 transition-colors',
                        isDragging ? 'bg-brand-500/10 text-brand-500' : 'bg-surface-overlay text-text-faint',
                    ].join(' ')}>
                        {isUploading
                            ? <Loader2 className="w-6 h-6 animate-spin text-brand-500" />
                            : <Upload className="w-6 h-6" />
                        }
                    </div>

                    <p className="text-sm font-medium text-text-primary mb-1">
                        {isUploading ? 'Uploading...' : 'Drag & drop your deck here'}
                    </p>
                    <p className="text-text-faint text-xs mb-6">
                        PDF, PPTX, or PPT
                    </p>

                    {!isUploading && (
                        <DGButton variant="primary" size="sm" className="pointer-events-none">
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
                <div className="mt-4 max-w-xl w-full rounded-lg border border-status-error/20 bg-status-error/5 px-4 py-3">
                    <p className="text-status-error text-sm">{error}</p>
                </div>
            )}
        </div>
    );
};
