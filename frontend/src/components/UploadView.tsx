import React, { useCallback, useState } from 'react';
import { UploadCloud, FileText, Loader2, AlertCircle } from 'lucide-react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';
import { uploadDeck, UploadResponse } from '../api/client';

interface UploadViewProps {
    onUploadComplete: (sessionId: string) => void;
}

export const UploadView: React.FC<UploadViewProps> = ({ onUploadComplete }) => {
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

    const processFile = async (file: File) => {
        if (!file.name.endsWith('.pdf') && !file.name.endsWith('.pptx')) {
            setError('Only PDF and PPTX files are supported.');
            return;
        }

        setIsUploading(true);
        try {
            const response = await uploadDeck(file);
            onUploadComplete(response.session_id);
        } catch (err) {
            console.error(err);
            setError('Failed to upload deck. Please try again.');
        } finally {
            setIsUploading(false);
        }
    };

    return (
        <div className="flex flex-col items-center justify-center min-h-[60vh] w-full max-w-2xl mx-auto p-6">
            <div className="text-center mb-10">
                <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent mb-4">
                    Demo Gauntlet
                </h1>
                <p className="text-gray-400 text-lg">
                    Upload your pitch deck to face the ultimate AI challenger.
                </p>
            </div>

            <div
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
                className={twMerge(
                    "w-full border-2 border-dashed rounded-2xl p-12 transition-all duration-300 flex flex-col items-center justify-center cursor-pointer group",
                    isDragging
                        ? "border-blue-500 bg-blue-500/10 scale-[1.02]"
                        : "border-gray-700 hover:border-blue-400 hover:bg-gray-800/50",
                    isUploading && "pointer-events-none opacity-50"
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
                    <div className="flex flex-col items-center animate-pulse">
                        <Loader2 className="w-16 h-16 text-blue-500 animate-spin mb-4" />
                        <p className="text-blue-400 font-medium">Ingesting Deck...</p>
                        <p className="text-xs text-gray-500 mt-2">Parsing slides, generating embeddings...</p>
                    </div>
                ) : (
                    <label htmlFor="file-upload" className="flex flex-col items-center cursor-pointer w-full h-full">
                        <div className="p-4 rounded-full bg-gray-800 group-hover:bg-blue-500/20 transition-colors mb-4">
                            <UploadCloud className="w-12 h-12 text-gray-400 group-hover:text-blue-400 transition-colors" />
                        </div>
                        <p className="text-xl font-semibold text-gray-200 mb-2">
                            Drag & drop or click to upload
                        </p>
                        <p className="text-sm text-gray-500">
                            Supports PDF and PPTX
                        </p>
                    </label>
                )}
            </div>

            {error && (
                <div className="mt-6 p-4 bg-red-500/10 border border-red-500/20 rounded-lg flex items-center text-red-400">
                    <AlertCircle className="w-5 h-5 mr-2" />
                    {error}
                </div>
            )}
        </div>
    );
};
