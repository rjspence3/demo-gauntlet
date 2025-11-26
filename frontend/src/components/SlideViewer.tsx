import React from 'react';
import { Slide } from '../api/client';
import { ChevronLeft, ChevronRight, FileText } from 'lucide-react';
import { clsx } from 'clsx';

interface SlideViewerProps {
    slide: Slide;
    currentSlideIndex: number;
    totalSlides: number;
    onNext: () => void;
    onPrev: () => void;
    onFinish: () => void;
}

export const SlideViewer: React.FC<SlideViewerProps> = ({
    slide,
    currentSlideIndex,
    totalSlides,
    onNext,
    onPrev,
    onFinish,
}) => {
    return (
        <div className="bg-white text-black rounded-xl shadow-2xl overflow-hidden flex flex-col h-[500px] w-full max-w-3xl border-4 border-gray-800 relative">
            {/* Slide Header */}
            <div className="bg-gray-100 p-4 border-b border-gray-300 flex justify-between items-center">
                <h2 className="text-xl font-bold truncate pr-4">{slide.title || "Untitled Slide"}</h2>
                <div className="flex items-center space-x-4">
                    <span className="text-sm font-mono text-gray-500">
                        {currentSlideIndex + 1} / {totalSlides}
                    </span>
                    <button
                        onClick={onFinish}
                        className="text-xs bg-red-600 hover:bg-red-700 text-white px-3 py-1 rounded transition-colors"
                    >
                        Finish & Report
                    </button>
                </div>
            </div>

            {/* Slide Content */}
            <div className="flex-1 p-8 overflow-y-auto bg-white">
                <div className="prose prose-lg max-w-none">
                    {slide.text ? (
                        <p className="whitespace-pre-wrap leading-relaxed">{slide.text}</p>
                    ) : (
                        <div className="flex flex-col items-center justify-center h-full text-gray-400">
                            <FileText className="w-12 h-12 mb-2 opacity-20" />
                            <p>No text content detected.</p>
                        </div>
                    )}
                </div>
            </div>

            {/* Slide Footer / Controls */}
            <div className="bg-gray-900 text-white p-4 flex justify-between items-center">
                <button
                    onClick={onPrev}
                    disabled={currentSlideIndex === 0}
                    className="p-2 rounded hover:bg-gray-700 disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
                >
                    <ChevronLeft className="w-6 h-6" />
                </button>

                <div className="flex space-x-2">
                    {slide.tags.map((tag, i) => (
                        <span key={i} className="text-xs px-2 py-1 bg-gray-700 rounded-full text-gray-300">
                            {tag}
                        </span>
                    ))}
                </div>

                <button
                    onClick={onNext}
                    disabled={currentSlideIndex === totalSlides - 1}
                    className="p-2 rounded hover:bg-gray-700 disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
                >
                    <ChevronRight className="w-6 h-6" />
                </button>
            </div>
        </div>
    );
};
