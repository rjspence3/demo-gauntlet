import React, { useEffect, useState } from 'react';
import { getSlides, listPersonas, getChallenges, submitAnswer, Slide, ChallengerPersona, Challenge, ScoreResponse } from '../api/client';
import { SlideViewer } from './SlideViewer';
import { ChallengerDetail } from './ChallengerDetail';
import { Loader2, User, MessageSquare, Send, AlertTriangle, Info, Zap, ArrowRight } from 'lucide-react';
import { cn } from '../lib/utils';
import { DGCard, DGButton, DGIconButton } from './ui';

/**
 * Props for the DemoRoom component.
 */
interface DemoRoomProps {
    /** The current session ID. */
    sessionId: string;
    /** List of IDs of selected personas. */
    selectedPersonaIds: string[];
    /** Callback when the simulation is finished. */
    onFinish: () => void;
}

/**
 * Main simulation component where the user interacts with challengers.
 */
export const DemoRoom: React.FC<DemoRoomProps> = ({ sessionId, selectedPersonaIds, onFinish }) => {
    const [slides, setSlides] = useState<Slide[]>([]);
    const [personas, setPersonas] = useState<ChallengerPersona[]>([]);
    const [activePersona, setActivePersona] = useState<ChallengerPersona | null>(null);
    const [currentSlideIndex, setCurrentSlideIndex] = useState(0);
    const [loading, setLoading] = useState(true);

    // Active challenges for the current slide
    const [activeChallenge, setActiveChallenge] = useState<Challenge | null>(null);
    const [isGenerating, setIsGenerating] = useState(false);
    const [userResponse, setUserResponse] = useState("");
    const [scoreResult, setScoreResult] = useState<ScoreResponse | null>(null);
    const [isSubmitting, setIsSubmitting] = useState(false);

    // Evidence Inspector State
    const [showEvidence, setShowEvidence] = useState(false);

    // Load initial data and challenges
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

    // Trigger challenge when slide changes
    useEffect(() => {
        if (slides.length === 0 || personas.length === 0) return;

        const triggerChallenge = () => {
            setActiveChallenge(null);
            setActivePersona(null);
            setUserResponse("");
            setScoreResult(null);
            setShowEvidence(false);

            const currentSlide = slides[currentSlideIndex];

            // Find challenges for this slide
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
    }, [currentSlideIndex, sessionId, slides.length, personas, sessionChallenges]);

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
                <Loader2 className="w-12 sm:w-16 h-12 sm:h-16 text-cyan-400 animate-spin mb-4" />
                <p className="text-slate-400 font-mono animate-pulse text-sm sm:text-base">Initializing Simulation...</p>
            </div>
        );
    }

    if (slides.length === 0) {
        return (
            <DGCard className="text-center mt-20 p-6 sm:p-8 max-w-md mx-auto border-rose-500/30">
                <AlertTriangle className="w-10 sm:w-12 h-10 sm:h-12 mx-auto mb-4 text-rose-500" />
                <p className="text-rose-400 font-mono text-sm sm:text-base">No slides found. Please upload a valid deck.</p>
            </DGCard>
        );
    }

    const currentSlide = slides[currentSlideIndex];

    return (
        <div className="flex flex-col lg:flex-row min-h-[calc(100vh-8rem)] gap-4 lg:gap-8">

            {/* Left Panel: Slide Viewer */}
            <div className="w-full lg:w-[58%] flex flex-col">
                <div className="flex-grow relative rounded-xl overflow-hidden h-[350px] sm:h-[450px] lg:h-auto">
                    <SlideViewer
                        slide={currentSlide}
                        currentSlideIndex={currentSlideIndex}
                        totalSlides={slides.length}
                        onNext={handleNext}
                        onPrev={handlePrev}
                        onFinish={onFinish}
                    />
                </div>

                {/* Slide Progress - Mobile */}
                <div className="mt-3 flex justify-center items-center px-4 lg:hidden">
                    <span className="text-xs text-slate-500 font-mono">
                        SLIDE {currentSlideIndex + 1} / {slides.length}
                    </span>
                </div>
            </div>

            {/* Right Panel: Challenger Interaction */}
            <div className="w-full lg:w-[42%] flex flex-col min-h-[400px] lg:min-h-0">
                <DGCard className="flex-grow flex flex-col overflow-hidden">

                    {/* Minimal Header - personas as dots, active one named */}
                    <div className="px-4 sm:px-5 py-3 border-b border-slate-800/50 flex items-center justify-between">
                        <div className="flex items-center gap-3">
                            <div className="flex items-center gap-1.5">
                                {personas.map(p => (
                                    <div
                                        key={p.id}
                                        className={cn(
                                            "w-2.5 h-2.5 rounded-full transition-all",
                                            activePersona?.id === p.id
                                                ? "bg-cyan-400 ring-2 ring-cyan-400/30"
                                                : "bg-slate-600"
                                        )}
                                        title={p.name}
                                    />
                                ))}
                            </div>
                            {activePersona && (
                                <span className="text-sm font-medium text-white">
                                    {activePersona.name}
                                </span>
                            )}
                        </div>
                        <div className="flex items-center gap-3">
                            <DGButton
                                variant="ghost"
                                size="sm"
                                onClick={onFinish}
                                className="text-xs text-slate-400 hover:text-white px-2 py-1 h-auto"
                            >
                                Ready for Recommendation?
                                <ArrowRight className="w-3 h-3 ml-1" />
                            </DGButton>
                            <div className="flex items-center gap-1.5 hidden sm:flex">
                                <div className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                                <span className="text-[10px] text-slate-500 font-mono uppercase tracking-wider">Live</span>
                            </div>
                        </div>
                    </div>

                    {/* Interaction Area */}
                    <div className="flex-grow p-4 sm:p-6 overflow-y-auto flex flex-col">

                        {/* Challenge Question - PRIMARY FOCAL POINT */}
                        {activeChallenge ? (
                            <div className="animate-fade-in mb-auto">
                                {/* Challenger identity */}
                                <div className="flex items-center gap-2 mb-3">
                                    <div className="w-8 h-8 rounded-full bg-cyan-400/10 flex items-center justify-center">
                                        <MessageSquare className="w-4 h-4 text-cyan-400" />
                                    </div>
                                    <span className="text-xs font-medium text-slate-400">
                                        {activePersona?.role || 'Challenger'}
                                    </span>
                                </div>

                                {/* The Question - HERO ELEMENT */}
                                <div className="relative group">
                                    <div className="absolute -inset-px bg-gradient-to-r from-cyan-400/20 to-transparent rounded-xl opacity-0 group-hover:opacity-100 transition-opacity" />
                                    <DGCard variant="bordered" className="relative p-4 sm:p-5 border-slate-700/50">
                                        <p className="text-base sm:text-lg text-white leading-relaxed font-medium">
                                            {activeChallenge.question}
                                        </p>
                                        <div className="absolute top-3 right-3 opacity-0 group-hover:opacity-100 transition-opacity">
                                            <DGIconButton
                                                icon={<Info className="w-4 h-4" />}
                                                ariaLabel="View evidence details"
                                                tooltip="Inspect Evidence"
                                                size="sm"
                                                onClick={() => setShowEvidence(true)}
                                            />
                                        </div>
                                    </DGCard>
                                </div>
                            </div>
                        ) : isGenerating ? (
                            <div className="flex-grow flex items-center justify-center">
                                <div className="flex items-center gap-3 text-slate-400">
                                    <Loader2 className="w-5 h-5 animate-spin" />
                                    <span className="text-sm font-mono">Analyzing slide...</span>
                                </div>
                            </div>
                        ) : (
                            <div className="flex-grow flex flex-col items-center justify-center text-center px-4">
                                <div className="w-12 h-12 rounded-full bg-slate-800/50 flex items-center justify-center mb-3">
                                    <Zap className="w-5 h-5 text-slate-600" />
                                </div>
                                <p className="text-slate-500 text-sm">No challenge on this slide</p>
                                <p className="text-slate-600 text-xs mt-1">Navigate to trigger questions</p>
                            </div>
                        )}

                        {/* Spacer to push response/score to bottom when challenge exists */}
                        {activeChallenge && <div className="flex-grow min-h-4" />}

                        {/* User Response Bubble */}
                        {scoreResult && userResponse && (
                            <div className="flex justify-end mb-4 animate-fade-in">
                                <div className="max-w-[85%]">
                                    <div className="bg-slate-800/80 rounded-xl rounded-tr-sm px-4 py-3">
                                        <p className="text-slate-200 text-sm leading-relaxed">{userResponse}</p>
                                    </div>
                                    <span className="text-[10px] text-slate-600 mt-1 block text-right mr-1">Your answer</span>
                                </div>
                            </div>
                        )}

                        {/* Evaluation Result - Secondary prominence */}
                        {scoreResult && (
                            <DGCard className={cn(
                                "animate-slide-up",
                                scoreResult.score >= 70
                                    ? "bg-emerald-500/10 border-emerald-500/30"
                                    : "bg-amber-500/10 border-amber-500/30"
                            )}>
                                <div className="p-4 sm:p-5">
                                    <div className="flex items-baseline justify-between mb-2">
                                        <span className="text-xs font-bold uppercase tracking-wider text-slate-400">Score</span>
                                        <span className={cn(
                                            "text-3xl sm:text-4xl font-bold tabular-nums",
                                            scoreResult.score >= 70 ? "text-emerald-400" : "text-amber-400"
                                        )}>
                                            {scoreResult.score}
                                        </span>
                                    </div>
                                    <p className="text-sm text-slate-300 leading-relaxed mb-4">{scoreResult.feedback}</p>
                                    <DGButton
                                        variant="secondary"
                                        size="sm"
                                        onClick={handleNext}
                                        className="w-full"
                                    >
                                        {currentSlideIndex < slides.length - 1 ? 'Next Slide' : 'View Results'}
                                    </DGButton>
                                </div>
                            </DGCard>
                        )}
                    </div>

                    {/* Input Area - Anchored at bottom */}
                    <div className={cn(
                        "p-4 sm:p-5 border-t border-slate-800/50 bg-slate-900/30",
                        (!activeChallenge || scoreResult) && "opacity-50 pointer-events-none"
                    )}>
                        <div className="relative">
                            <input
                                type="text"
                                value={userResponse}
                                onChange={(e) => setUserResponse(e.target.value)}
                                placeholder={activeChallenge && !scoreResult ? "Type your response..." : "Waiting for challenge..."}
                                disabled={!activeChallenge || !!scoreResult || isSubmitting}
                                className="w-full bg-slate-800/80 border border-slate-700/50 rounded-xl py-3.5 px-4 pr-14 text-white placeholder-slate-500 focus:outline-none focus:border-cyan-400/50 focus:ring-1 focus:ring-cyan-400/50 transition-all disabled:opacity-60 text-sm sm:text-base"
                                onKeyDown={(e) => e.key === 'Enter' && !e.shiftKey && handleSubmitResponse()}
                            />
                            <div className="absolute right-2 top-1/2 -translate-y-1/2">
                                <DGIconButton
                                    icon={isSubmitting ? <Loader2 className="w-5 h-5 animate-spin" /> : <Send className="w-5 h-5" />}
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
