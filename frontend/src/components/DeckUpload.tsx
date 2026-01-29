import React, { useState, useCallback } from 'react';

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
            'application/vnd.openxmlformats-officedocument.presentationml.presentation', // pptx
            'application/vnd.ms-powerpoint' // ppt
        ];

        if (!validTypes.includes(file.type) && !file.name.endsWith('.pptx') && !file.name.endsWith('.ppt') && !file.name.endsWith('.pdf')) {
            setError('Please upload a valid PDF or PowerPoint file.');
            return;
        }

        onUploadComplete(file);
    };

    return (
        <div className="flex flex-col items-center justify-center min-h-[600px] w-full max-w-4xl mx-auto p-6">
            <div className="text-center mb-10">
                <h1 className="text-4xl font-bold text-gray-900 mb-4 tracking-tight">
                    Ready to run the gauntlet?
                </h1>
                <p className="text-xl text-gray-600">
                    Upload your deck to benchmark your demo readiness.
                </p>
            </div>

            <div
                className={`
          w-full max-w-2xl h-80 rounded-2xl border-2 border-dashed transition-all duration-300 ease-in-out
          flex flex-col items-center justify-center cursor-pointer
          ${isDragging
                        ? 'border-blue-500 bg-blue-50 scale-[1.02] shadow-lg'
                        : 'border-gray-300 hover:border-gray-400 bg-white hover:bg-gray-50'
                    }
        `}
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
                onClick={() => document.getElementById('file-upload')?.click()}
            >
                <div className="text-center p-8">
                    <div className="w-16 h-16 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center mx-auto mb-6">
                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className="w-8 h-8">
                            <path strokeLinecap="round" strokeLinejoin="round" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5m-13.5-9L12 3m0 0l4.5 4.5M12 3v13.5" />
                        </svg>
                    </div>

                    <h3 className="text-lg font-semibold text-gray-900 mb-2">
                        Drag & drop your deck here
                    </h3>
                    <p className="text-gray-500 mb-6">
                        Supports PDF, PPTX, or PPT
                    </p>

                    <button className="px-6 py-2.5 bg-gray-900 text-white rounded-lg font-medium hover:bg-black transition-colors shadow-sm">
                        Select File
                    </button>

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
                <div className="mt-6 p-4 bg-red-50 text-red-700 rounded-lg flex items-center animate-fade-in">
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" className="w-5 h-5 mr-2">
                        <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.28 7.22a.75.75 0 00-1.06 1.06L8.94 10l-1.72 1.72a.75.75 0 101.06 1.06L10 11.06l1.72 1.72a.75.75 0 101.06-1.06L11.06 10l1.72-1.72a.75.75 0 00-1.06-1.06L10 8.94 8.28 7.22z" clipRule="evenodd" />
                    </svg>
                    {error}
                </div>
            )}
        </div>
    );
};
