import React, { useEffect, useState, useCallback } from 'react';
import { getSlides, listPersonas, generateChallenges, submitAnswer, Slide, ChallengerPersona, Challenge, ScoreResponse } from '../api/client';
import { SlideViewer } from './SlideViewer';
import { Loader2, User, MessageSquare, Send, CheckCircle, AlertCircle } from 'lucide-react';
import { clsx } from 'clsx';

interface DemoRoomProps {
    sessionId: string;
    onFinish: () => void;
}

export const DemoRoom: React.FC<DemoRoomProps> = ({ sessionId, onFinish }) => {
    const [slides, setSlides] = useState<Slide[]>([]);
    const [personas, setPersonas] = useState<ChallengerPersona[]>([]);
    const [currentSlideIndex, setCurrentSlideIndex] = useState(0);
    const [loading, setLoading] = useState(true);

    // Active challenges for the current slide
    const [activeChallenge, setActiveChallenge] = useState<Challenge | null>(null);
    const [isGenerating, setIsGenerating] = useState(false);
    const [userResponse, setUserResponse] = useState("");
    const [scoreResult, setScoreResult] = useState<ScoreResponse | null>(null);
    const [isSubmitting, setIsSubmitting] = useState(false);

    // Load initial data
    useEffect(() => {
        const init = async () => {
            try {
                const [slidesData, personasData] = await Promise.all([
                    getSlides(sessionId),
                    listPersonas()
                ]);
                setSlides(slidesData);
                setPersonas(personasData);
            } catch (err) {
                console.error("Failed to load demo room data", err);
            } finally {
                setLoading(false);
            }
        };
        init();
    }, [sessionId]);

    // Generate challenge when slide changes (simulated "random" trigger)
    useEffect(() => {
        if (slides.length === 0 || personas.length === 0) return;

        const triggerChallenge = async () => {
            setActiveChallenge(null);
            setUserResponse("");

            // 50% chance to trigger a challenge on slide load (for demo purposes, make it 100% or button triggered)
            // Let's make it auto-trigger for now to show off the feature
            setIsGenerating(true);
            try {
                // Pick a random persona
                const randomPersona = personas[Math.floor(Math.random() * personas.length)];
                const currentSlide = slides[currentSlideIndex];

                const challenges = await generateChallenges(
                    sessionId,
                    randomPersona.id,
                    currentSlide.index,
                    currentSlide.text
                );

                if (challenges.length > 0) {
                    setActiveChallenge(challenges[0]);
                }
            } catch (err) {
                console.error("Failed to generate challenge", err);
            } finally {
                setIsGenerating(false);
            }
        };

        triggerChallenge();
    }, [currentSlideIndex, sessionId, slides.length, personas.length]); // Dependencies need care to avoid loops

    const handleNext = () => {
        if (currentSlideIndex < slides.length - 1) {
            setCurrentSlideIndex(prev => prev + 1);
        }
    };

    const handlePrev = () => {
        if (currentSlideIndex > 0) {
            setCurrentSlideIndex(prev => prev - 1);
        }
    };

    const handleSubmitResponse = async () => {
        if (!activeChallenge || !userResponse.trim()) return;

        setIsSubmitting(true);
        try {
            const result = await submitAnswer(
                sessionId,
                activeChallenge.persona_id,
                activeChallenge.id,
                userResponse,
                activeChallenge.ideal_answer
            );
            setScoreResult(result);
        } catch (err) {
            console.error("Failed to submit answer", err);
        } finally {
            setIsSubmitting(false);
        }
    };

    const handleDismissChallenge = () => {
        setActiveChallenge(null);
        setScoreResult(null);
        setUserResponse("");
    };

    if (loading) {
        return (
            <div className="flex flex-col items-center justify-center h-[60vh]">
                <Loader2 className="w-12 h-12 text-blue-500 animate-spin mb-4" />
                <p className="text-gray-400">Preparing the Gauntlet...</p>
            </div>
        );
    }

    if (slides.length === 0) {
        return (
            <div className="text-center text-red-400 mt-20">
                No slides found. Please upload a valid deck.
            </div>
        );
    }

    const currentSlide = slides[currentSlideIndex];

    return (
        <div className="flex flex-col items-center justify-center min-h-[80vh] relative p-8">

            {/* Main Stage */}
            <div className="relative z-10">
                <SlideViewer
                    slide={currentSlide}
                    currentSlideIndex={currentSlideIndex}
                    totalSlides={slides.length}
                    onNext={handleNext}
                    onPrev={handlePrev}
                    onFinish={onFinish}
                />
            </div>

            {/* Personas (Avatars) - Positioned around */}
            <div className="absolute top-10 left-10 flex flex-col items-center opacity-50 hover:opacity-100 transition-opacity">
                <div className="w-16 h-16 bg-gray-700 rounded-full flex items-center justify-center border-2 border-gray-500">
                    <User className="w-8 h-8 text-gray-300" />
                </div>
                <span className="text-xs text-gray-400 mt-2">The Skeptic</span>
            </div>

            <div className="absolute top-10 right-10 flex flex-col items-center opacity-50 hover:opacity-100 transition-opacity">
                <div className="w-16 h-16 bg-gray-700 rounded-full flex items-center justify-center border-2 border-gray-500">
                    <User className="w-8 h-8 text-gray-300" />
                </div>
                <span className="text-xs text-gray-400 mt-2">Budget Hawk</span>
            </div>

            {/* Active Challenge Overlay / Bubble */}
            {activeChallenge && (
                <div className="absolute -bottom-20 left-1/2 transform -translate-x-1/2 w-full max-w-2xl animate-in slide-in-from-bottom-10 duration-500 z-50">
                    <div className="bg-gray-900/95 backdrop-blur-xl border border-red-500/50 rounded-2xl p-6 shadow-2xl shadow-red-900/20">
                        <div className="flex items-start space-x-4">
                            <div className="bg-red-500/20 p-3 rounded-full">
                                <MessageSquare className="w-6 h-6 text-red-400" />
                            </div>
                            <div className="flex-1">
                                <div className="flex justify-between items-center mb-2">
                                    <h3 className="font-bold text-red-400">Challenger Interruption!</h3>
                                    <span className="text-xs bg-gray-800 px-2 py-1 rounded text-gray-400">
                                        {personas.find(p => p.id === activeChallenge.persona_id)?.name || "Unknown"}
                                    </span>
                                </div>
                                <p className="text-lg text-white mb-4 font-medium">
                                    "{activeChallenge.question}"
                                </p>

                                <div className="relative">
                                    {!scoreResult ? (
                                        <>
                                            <input
                                                type="text"
                                                value={userResponse}
                                                onChange={(e) => setUserResponse(e.target.value)}
                                                placeholder="Type your response..."
                                                disabled={isSubmitting}
                                                className="w-full bg-gray-800 border border-gray-700 rounded-lg py-3 px-4 pr-12 text-white focus:outline-none focus:border-blue-500 transition-colors disabled:opacity-50"
                                                onKeyDown={(e) => e.key === 'Enter' && handleSubmitResponse()}
                                            />
                                            <button
                                                onClick={handleSubmitResponse}
                                                disabled={isSubmitting || !userResponse.trim()}
                                                className="absolute right-2 top-1/2 transform -translate-y-1/2 p-2 text-blue-400 hover:text-blue-300 disabled:opacity-30"
                                            >
                                                {isSubmitting ? <Loader2 className="w-5 h-5 animate-spin" /> : <Send className="w-5 h-5" />}
                                            </button>
                                        </>
                                    ) : (
                                        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700 animate-in fade-in zoom-in duration-300">
                                            <div className="flex items-center justify-between mb-2">
                                                <div className="flex items-center space-x-2">
                                                    {scoreResult.score >= 70 ? (
                                                        <CheckCircle className="w-5 h-5 text-green-500" />
                                                    ) : (
                                                        <AlertCircle className="w-5 h-5 text-yellow-500" />
                                                    )}
                                                    <span className={clsx(
                                                        "font-bold text-lg",
                                                        scoreResult.score >= 85 ? "text-green-400" :
                                                            scoreResult.score >= 70 ? "text-green-300" :
                                                                scoreResult.score >= 50 ? "text-yellow-400" : "text-red-400"
                                                    )}>
                                                        Score: {scoreResult.score}/100
                                                    </span>
                                                </div>
                                                <button
                                                    onClick={handleDismissChallenge}
                                                    className="text-xs bg-gray-700 hover:bg-gray-600 px-3 py-1 rounded text-white transition-colors"
                                                >
                                                    Continue
                                                </button>
                                            </div>
                                            <p className="text-gray-300 text-sm mb-3">{scoreResult.feedback}</p>
                                            <div className="text-xs text-gray-500 border-t border-gray-700 pt-2">
                                                <span className="font-semibold text-gray-400">Ideal Answer:</span> {activeChallenge.ideal_answer}
                                            </div>
                                        </div>
                                    )}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            )}

            {isGenerating && !activeChallenge && (
                <div className="absolute bottom-10 left-1/2 transform -translate-x-1/2 bg-gray-800/80 px-4 py-2 rounded-full flex items-center space-x-2">
                    <Loader2 className="w-4 h-4 animate-spin text-blue-400" />
                    <span className="text-sm text-gray-300">Analyzing slide...</span>
                </div>
            )}
        </div>
    );
};
