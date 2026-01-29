import React from 'react';
import { Slide } from '../api/client';
import { ChevronLeft, ChevronRight, FileText } from 'lucide-react';
import { cn } from '../lib/utils';
import { DGCard, DGButton, DGIconButton, DGTag } from './ui';

/**
 * Props for the SlideViewer component.
 */
interface SlideViewerProps {
    /** The slide to display. */
    slide: Slide;
    /** The index of the current slide (0-based). */
    currentSlideIndex: number;
    /** Total number of slides in the deck. */
    totalSlides: number;
    /** Callback to go to the next slide. */
    onNext: () => void;
    /** Callback to go to the previous slide. */
    onPrev: () => void;
    /** Callback to finish the session early. */
    onFinish: () => void;
}

/**
 * Component for displaying the current slide content.
 */
export const SlideViewer: React.FC<SlideViewerProps> = ({
    slide,
    currentSlideIndex,
    totalSlides,
    onNext,
    onPrev,
    onFinish,
}) => {
    return (
        <DGCard variant="bordered" className="flex flex-col h-full w-full overflow-hidden">
            {/* Slide Header */}
            <div className="bg-slate-800/50 p-3 sm:p-4 border-b border-slate-700 flex justify-between items-center gap-2">
                <h2 className="text-base sm:text-xl font-bold text-white truncate flex-1">
                    {slide.title || "Untitled Slide"}
                </h2>
                <div className="flex items-center space-x-2 sm:space-x-4 flex-shrink-0">
                    <span className="text-xs sm:text-sm font-mono text-slate-400">
                        {currentSlideIndex + 1} / {totalSlides}
                    </span>
                    <DGButton
                        variant="danger"
                        size="sm"
                        onClick={onFinish}
                        className="hidden sm:flex"
                    >
                        Finish & Report
                    </DGButton>
                    <DGButton
                        variant="danger"
                        size="sm"
                        onClick={onFinish}
                        className="sm:hidden text-xs px-2"
                    >
                        Finish
                    </DGButton>
                </div>
            </div>

            {/* Slide Content */}
            <div className="flex-1 p-4 sm:p-8 overflow-y-auto bg-slate-900/50">
                <div className="max-w-none">
                    {slide.text ? (
                        <p className="whitespace-pre-wrap leading-relaxed text-slate-200 text-sm sm:text-base">
                            {slide.text}
                        </p>
                    ) : (
                        <div className="flex flex-col items-center justify-center h-full text-slate-500 py-12">
                            <FileText className="w-10 sm:w-12 h-10 sm:h-12 mb-2 opacity-30" />
                            <p className="text-sm">No text content detected.</p>
                        </div>
                    )}
                </div>
            </div>

            {/* Slide Footer / Controls */}
            <div className="bg-slate-800 p-3 sm:p-4 flex justify-between items-center border-t border-slate-700">
                <DGIconButton
                    icon={<ChevronLeft className="w-5 sm:w-6 h-5 sm:h-6" />}
                    ariaLabel="Previous slide"
                    onClick={onPrev}
                    disabled={currentSlideIndex === 0}
                    size="sm"
                />

                <div className="flex flex-wrap justify-center gap-1 sm:gap-2 max-w-[60%]">
                    {slide.tags.slice(0, 3).map((tag, i) => (
                        <DGTag key={i}>{tag}</DGTag>
                    ))}
                    {slide.tags.length > 3 && (
                        <span className="text-xs text-slate-500">+{slide.tags.length - 3}</span>
                    )}
                </div>

                <DGIconButton
                    icon={<ChevronRight className="w-5 sm:w-6 h-5 sm:h-6" />}
                    ariaLabel="Next slide"
                    onClick={onNext}
                    disabled={currentSlideIndex === totalSlides - 1}
                    size="sm"
                />
            </div>
        </DGCard>
    );
};
