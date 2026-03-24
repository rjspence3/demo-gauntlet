import React from 'react';
import { Slide } from '../api/client';
import { ChevronLeft, ChevronRight, FileText } from 'lucide-react';
import { DGButton, DGIconButton, DGTag } from './ui';

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
        <div className="flex flex-col h-full w-full overflow-hidden bg-surface border border-border rounded-xl">
            {/* Slide Header */}
            <div className="px-4 py-3 border-b border-border flex justify-between items-center gap-2">
                <h2 className="text-sm font-medium text-text-primary truncate flex-1">
                    {slide.title || "Untitled Slide"}
                </h2>
                <div className="flex items-center gap-3 flex-shrink-0">
                    <span className="text-xs text-text-faint font-mono tabular-nums">
                        {currentSlideIndex + 1}/{totalSlides}
                    </span>
                    <DGButton
                        variant="ghost"
                        size="sm"
                        onClick={onFinish}
                        className="text-xs"
                    >
                        Finish
                    </DGButton>
                </div>
            </div>

            {/* Slide Content */}
            <div className="flex-1 p-5 sm:p-8 overflow-y-auto">
                {slide.text ? (
                    <p className="whitespace-pre-wrap leading-relaxed text-text-secondary text-sm">
                        {slide.text}
                    </p>
                ) : (
                    <div className="flex flex-col items-center justify-center h-full text-text-faint py-12">
                        <FileText className="w-10 h-10 mb-2 opacity-30" />
                        <p className="text-sm">No text content detected.</p>
                    </div>
                )}
            </div>

            {/* Slide Footer */}
            <div className="px-4 py-3 flex justify-between items-center border-t border-border">
                <DGIconButton
                    icon={<ChevronLeft className="w-4 h-4" />}
                    ariaLabel="Previous slide"
                    onClick={onPrev}
                    disabled={currentSlideIndex === 0}
                    size="sm"
                />

                <div className="flex flex-wrap justify-center gap-1.5 max-w-[60%]">
                    {slide.tags.slice(0, 3).map((tag, i) => (
                        <DGTag key={i}>{tag}</DGTag>
                    ))}
                    {slide.tags.length > 3 && (
                        <span className="text-xs text-text-faint">+{slide.tags.length - 3}</span>
                    )}
                </div>

                <DGIconButton
                    icon={<ChevronRight className="w-4 h-4" />}
                    ariaLabel="Next slide"
                    onClick={onNext}
                    disabled={currentSlideIndex === totalSlides - 1}
                    size="sm"
                />
            </div>
        </div>
    );
};
