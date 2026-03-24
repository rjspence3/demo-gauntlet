import React, { useEffect, useState } from 'react';
import { getSlides, listPersonas, getChallenges, submitAnswer, Slide, ChallengerPersona, Challenge, ScoreResponse } from '../api/client';
import { SlideViewer } from './SlideViewer';
import { ChallengerDetail } from './ChallengerDetail';
import { Loader2, MessageSquare, Send, AlertTriangle, Info, ArrowRight } from 'lucide-react';
import { cn } from '../lib/utils';
import { DGCard, DGButton, DGIconButton } from './ui';

interface DemoRoomProps {
    sessionId: string;
    selectedPersonaIds: string[];
    onFinish: () => void;
}

export const DemoRoom: React.FC<DemoRoomProps> = ({ sessionId, selectedPersonaIds, onFinish }) => {
    const [slides, setSlides] = useState<Slide[]>([]);
    const [personas, setPersonas] = useState<ChallengerPersona[]>([]);
    const [activePersona, setActivePersona] = useState<ChallengerPersona | null>(null);
    const [currentSlideIndex, setCurrentSlideIndex] = useState(0);
    const [loading, setLoading] = useState(true);

    const [activeChallenge, setActiveChallenge] = useState<Challenge | null>(null);
    const [isGenerating, setIsGenerating] = useState(false);
    const [userResponse, setUserResponse] = useState("");
    const [scoreResult, setScoreResult] = useState<ScoreResponse | null>(null);
    const [isSubmitting, setIsSubmitting] = useState(false);

    const [showEvidence, setShowEvidence] = useState(false);

    const [sessionChallenges, setSessionChallenges] = useState<Challenge[]>([]);

    useEffect(() => {
        const init = async () => {
            try {
                const [slidesData, personasData] = await Promise.all([
                    getSlides(sessionId),
                    listPersonas()
                ]);
                setSlides(slidesData);
                const selected = personasData.filter(p => selectedPersonaIds.includes(p.id));
                setPersonas(selected);

                const challengesData = await getChallenges(sessionId);
                setSessionChallenges(challengesData);
            } catch (err) {
                console.error("Failed to load demo room data", err);
            } finally {
                setLoading(false);
            }
        };
        init();
    }, [sessionId, selectedPersonaIds]);

    useEffect(() => {
        if (slides.length === 0 || personas.length === 0) return;

        const triggerChallenge = () => {
            setActiveChallenge(null);
            setActivePersona(null);
            setUserResponse("");
            setScoreResult(null);
            setShowEvidence(false);

            const currentSlide = slides[currentSlideIndex];
            const slideChallenges = sessionChallenges.filter(c => c.slide_index === currentSlide.index);

            if (slideChallenges.length > 0) {
                const relevant = slideChallenges.filter(c => selectedPersonaIds.includes(c.persona_id));

                if (relevant.length > 0) {
                    const challenge = relevant[Math.floor(Math.random() * relevant.length)];
                    setActiveChallenge(challenge);
                    const persona = personas.find(p => p.id === challenge.persona_id);
                    setActivePersona(persona || null);
                }
            }
        };

        triggerChallenge();
    }, [currentSlideIndex, sessionId, slides.length, personas, sessionChallenges, selectedPersonaIds]);

    const handleNext = () => {
        if (currentSlideIndex < slides.length - 1) {
            setCurrentSlideIndex(prev => prev + 1);
        } else {
            onFinish();
        }
    };

    const handlePrev = () => {
        if (currentSlideIndex > 0) {
            setCurrentSlideIndex(prev => prev - 1);
        }
    };

    const handleSubmitResponse = async () => {
        if (!activeChallenge || !userResponse.trim() || !activePersona) return;

        setIsSubmitting(true);
        try {
            const result = await submitAnswer(
                sessionId,
                activePersona.id,
                activeChallenge.id,
                userResponse
            );
            setScoreResult(result);
        } catch (err) {
            console.error("Failed to submit answer", err);
        } finally {
            setIsSubmitting(false);
        }
    };

    if (loading) {
        return (
            <div className="flex flex-col items-center justify-center min-h-[60vh]">
                <Loader2 className="w-8 h-8 text-ai-500 animate-spin mb-3" />
                <p className="text-text-muted text-sm animate-soft-pulse">Loading simulation...</p>
            </div>
        );
    }

    if (slides.length === 0) {
        return (
            <div className="text-center mt-20 p-6 max-w-sm mx-auto">
                <AlertTriangle className="w-8 h-8 mx-auto mb-3 text-status-error" />
                <p className="text-status-error text-sm">No slides found. Please upload a valid deck.</p>
            </div>
        );
    }

    const currentSlide = slides[currentSlideIndex];

    return (
        <div className="flex flex-col lg:flex-row min-h-[calc(100vh-8rem)] gap-4">

            {/* Left Panel: Slide Viewer */}
            <div className="w-full lg:w-[55%] flex flex-col">
                <div className="flex-grow relative h-[350px] sm:h-[450px] lg:h-auto">
                    <SlideViewer
                        slide={currentSlide}
                        currentSlideIndex={currentSlideIndex}
                        totalSlides={slides.length}
                        onNext={handleNext}
                        onPrev={handlePrev}
                        onFinish={onFinish}
                    />
                </div>

                <div className="mt-2 flex justify-center items-center lg:hidden">
                    <span className="text-[10px] text-text-faint font-mono uppercase tracking-wider">
                        Slide {currentSlideIndex + 1} / {slides.length}
                    </span>
                </div>
            </div>

            {/* Right Panel: Challenger Interaction */}
            <div className="w-full lg:w-[45%] flex flex-col min-h-[400px] lg:min-h-0">
                <DGCard variant="default" className="flex-grow flex flex-col overflow-hidden">

                    {/* Header */}
                    <div className="px-4 py-3 border-b border-border flex items-center justify-between">
                        <div className="flex items-center gap-3">
                            <div className="flex items-center gap-1">
                                {personas.map(p => (
                                    <div
                                        key={p.id}
                                        className={cn(
                                            "w-2.5 h-2.5 rounded-full transition-all",
                                            activePersona?.id === p.id
                                                ? "bg-ai-500 ring-2 ring-ai-500/20"
                                                : "bg-text-faint/40"
                                        )}
                                        title={p.name}
                                    />
                                ))}
                            </div>
                            {activePersona && (
                                <span className="text-sm font-semibold text-text-primary">
                                    {activePersona.name}
                                </span>
                            )}
                        </div>
                        <div className="flex items-center gap-2">
                            <DGButton
                                variant="ghost"
                                size="sm"
                                onClick={onFinish}
                                className="text-xs"
                            >
                                Finish
                                <ArrowRight className="w-3 h-3 ml-1" />
                            </DGButton>
                            <div className="hidden sm:flex items-center gap-1.5">
                                <div className="w-1.5 h-1.5 rounded-full bg-status-success animate-soft-pulse" />
                                <span className="text-[10px] text-text-faint font-mono uppercase tracking-wider">Live</span>
                            </div>
                        </div>
                    </div>

                    {/* Interaction Area */}
                    <div className="flex-grow p-4 sm:p-5 overflow-y-auto flex flex-col">

                        {activeChallenge ? (
                            <div className="animate-fade-in mb-auto">
                                <div className="flex items-center gap-2 mb-3">
                                    <div className="w-7 h-7 rounded-lg bg-ai-50 flex items-center justify-center">
                                        <MessageSquare className="w-3.5 h-3.5 text-ai-500" />
                                    </div>
                                    <span className="text-xs font-medium text-ai-500 uppercase tracking-wide">
                                        {activePersona?.role || 'Challenger'}
                                    </span>
                                </div>

                                <div className="relative group">
                                    {/* Challenger message — indigo left border accent */}
                                    <div className="bg-ai-50/40 border border-ai-200/50 border-l-2 border-l-ai-400 rounded-xl p-4">
                                        <p className="text-sm sm:text-base text-text-primary leading-relaxed">
                                            {activeChallenge.question}
                                        </p>
                                        <div className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity">
                                            <DGIconButton
                                                icon={<Info className="w-3.5 h-3.5" />}
                                                ariaLabel="View evidence details"
                                                tooltip="Inspect Evidence"
                                                size="sm"
                                                onClick={() => setShowEvidence(true)}
                                            />
                                        </div>
                                    </div>
                                </div>
                            </div>
                        ) : isGenerating ? (
                            <div className="flex-grow flex items-center justify-center">
                                <div className="flex items-center gap-2 text-text-muted">
                                    <Loader2 className="w-4 h-4 animate-spin text-ai-500" />
                                    <span className="text-sm">Analyzing slide...</span>
                                </div>
                            </div>
                        ) : (
                            <div className="flex-grow flex flex-col items-center justify-center text-center px-4">
                                <p className="text-text-secondary text-sm">No objections on this slide</p>
                                <p className="text-text-faint text-xs mt-1">Navigate to the next slide</p>
                            </div>
                        )}

                        {activeChallenge && <div className="flex-grow min-h-4" />}

                        {/* User Response */}
                        {scoreResult && userResponse && (
                            <div className="flex justify-end mb-3 animate-fade-in">
                                <div className="max-w-[85%]">
                                    <div className="bg-white/60 border border-border rounded-xl rounded-tr-sm px-3 py-2.5">
                                        <p className="text-text-secondary text-sm leading-relaxed">{userResponse}</p>
                                    </div>
                                    <span className="text-[10px] text-text-faint mt-1 block text-right">Your answer</span>
                                </div>
                            </div>
                        )}

                        {/* Score Result */}
                        {scoreResult && (
                            <div className={cn(
                                "animate-slide-up rounded-xl border p-4",
                                scoreResult.score >= 70
                                    ? "border-status-success/20 bg-status-success/5"
                                    : "border-status-warning/20 bg-status-warning/5"
                            )}>
                                <div className="flex items-baseline justify-between mb-2">
                                    <span className="text-[10px] font-medium uppercase tracking-wider text-text-faint">Score</span>
                                    <span className={cn(
                                        "text-3xl font-bold tabular-nums",
                                        scoreResult.score >= 70 ? "text-status-success" : "text-status-warning"
                                    )}>
                                        {scoreResult.score}
                                    </span>
                                </div>
                                <p className="text-sm text-text-secondary leading-relaxed mb-3">{scoreResult.feedback}</p>
                                <DGButton
                                    variant="secondary"
                                    size="sm"
                                    onClick={handleNext}
                                    className="w-full"
                                >
                                    {currentSlideIndex < slides.length - 1 ? 'Next Slide' : 'View Results'}
                                </DGButton>
                            </div>
                        )}
                    </div>

                    {/* Input Area */}
                    <div className={cn(
                        "p-4 border-t border-border",
                        (!activeChallenge || scoreResult) && "opacity-40 pointer-events-none"
                    )}>
                        <div className="relative">
                            <textarea
                                rows={3}
                                value={userResponse}
                                onChange={(e) => setUserResponse(e.target.value)}
                                placeholder={activeChallenge && !scoreResult ? "Type your response... (Enter to submit)" : "Waiting for challenge..."}
                                disabled={!activeChallenge || !!scoreResult || isSubmitting}
                                className="w-full resize-none bg-white/80 backdrop-blur-sm border border-border-ai rounded-xl py-3 px-3 pr-12 text-text-primary placeholder-text-faint focus:outline-none focus:border-ai-400 focus:ring-2 focus:ring-ai-500/20 transition-all disabled:opacity-50 text-sm"
                                onKeyDown={(e) => {
                                    if (e.key === 'Enter' && !e.shiftKey) {
                                        e.preventDefault();
                                        handleSubmitResponse();
                                    }
                                }}
                            />
                            <div className="absolute right-2 bottom-2">
                                <DGIconButton
                                    icon={isSubmitting ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
                                    ariaLabel={isSubmitting ? "Submitting response" : "Submit response"}
                                    size="sm"
                                    variant={userResponse.trim() ? "active" : "default"}
                                    disabled={!activeChallenge || !!scoreResult || isSubmitting || !userResponse.trim()}
                                    onClick={handleSubmitResponse}
                                />
                            </div>
                        </div>
                    </div>

                </DGCard>
            </div>

            {/* Evidence Inspector Modal */}
            {showEvidence && activeChallenge && (
                <ChallengerDetail
                    challenge={activeChallenge}
                    onClose={() => setShowEvidence(false)}
                    chunks={activeChallenge.evidence?.chunks || []}
                    facts={activeChallenge.evidence?.facts || []}
                />
            )}

        </div>
    );
};
