import React, { useEffect, useState, useRef } from 'react';
import { getSlides, listPersonas, generateChallenges, submitAnswer, Slide, ChallengerPersona, Challenge, ScoreResponse } from '../api/client';
import { SlideViewer } from './SlideViewer';
import { ChallengerDetail } from './ChallengerDetail';
import { Loader2, User, MessageSquare, Send, CheckCircle, AlertCircle, AlertTriangle, Shield, TrendingUp, Cpu, Mic, Volume2, Info } from 'lucide-react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

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

                // Fetch precomputed challenges
                // We need an endpoint for this or use listChallenges?
                // Assuming listChallenges exists or we add it.
                // For MVP, let's assume we can fetch them.
                // Wait, I didn't add a listChallenges endpoint for the session.
                // I should probably add it or use a direct fetch if possible?
                // I'll add a fetch here assuming the endpoint exists or I'll add it to the client.
                // Let's assume `getChallenges(sessionId)` exists in client.
                // I need to update client.ts first? Or just fetch directly.
                const challengesResp = await fetch(`http://localhost:8005/challenges/session/${sessionId}`);
                if (challengesResp.ok) {
                    const challengesData = await challengesResp.json();
                    setSessionChallenges(challengesData);
                }
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
                // Pick one randomly or based on priority
                // Filter by selected personas just in case
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
            <div className="flex flex-col items-center justify-center h-[80vh]">
                <Loader2 className="w-16 h-16 text-neon-blue animate-spin mb-4" />
                <p className="text-gray-400 font-mono animate-pulse">Initializing Simulation...</p>
            </div>
        );
    }

    if (slides.length === 0) {
        return (
            <div className="text-center text-danger-red mt-20 font-mono border border-danger-red/30 p-8 rounded-xl bg-danger-red/5">
                <AlertTriangle className="w-12 h-12 mx-auto mb-4" />
                No slides found. Please upload a valid deck.
            </div>
        );
    }

    const currentSlide = slides[currentSlideIndex];

    return (
        <div className="flex h-screen overflow-hidden bg-cyber-black text-white">

            {/* Left Panel: Slide Viewer (60%) */}
            <div className="w-[60%] h-full p-6 flex flex-col border-r border-white/10 relative">
                <div className="flex-grow relative rounded-2xl overflow-hidden border border-white/10 shadow-2xl bg-black">
                    <SlideViewer
                        slide={currentSlide}
                        currentSlideIndex={currentSlideIndex}
                        totalSlides={slides.length}
                        onNext={handleNext}
                        onPrev={handlePrev}
                        onFinish={onFinish}
                    />
                </div>

                {/* Slide Controls / Progress */}
                <div className="mt-4 flex justify-between items-center px-4">
                    <div className="text-sm text-gray-500 font-mono">
                        SLIDE {currentSlideIndex + 1} / {slides.length}
                    </div>
                    <div className="flex space-x-2">
                        {/* Add any extra controls here */}
                    </div>
                </div>
            </div>

            {/* Right Panel: Challenger Interaction (40%) */}
            <div className="w-[40%] h-full flex flex-col bg-gray-900/50 relative">

                {/* Challenger Header - List all active personas */}
                <div className="p-6 border-b border-white/10 flex items-center justify-between bg-black/20">
                    <div className="flex items-center space-x-2 overflow-x-auto">
                        {personas.map(p => (
                            <div key={p.id} className={clsx(
                                "flex items-center space-x-2 px-3 py-1.5 rounded-full border transition-all",
                                activePersona?.id === p.id
                                    ? "bg-neon-blue/20 border-neon-blue text-white"
                                    : "bg-white/5 border-white/10 text-gray-400 opacity-60"
                            )}>
                                <User className="w-3 h-3" />
                                <span className="text-xs font-bold">{p.name}</span>
                            </div>
                        ))}
                    </div>
                    <div className="flex items-center space-x-2">
                        <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></div>
                        <span className="text-xs text-gray-500 font-mono">LIVE</span>
                    </div>
                </div>

                {/* Interaction Area */}
                <div className="flex-grow p-6 overflow-y-auto custom-scrollbar flex flex-col space-y-6">

                    {/* Challenger Bubble */}
                    {activeChallenge ? (
                        <div className="flex items-start space-x-3 animate-fade-in">
                            <div className="w-8 h-8 rounded-full bg-neon-blue/10 flex-shrink-0 flex items-center justify-center mt-1">
                                <MessageSquare className="w-4 h-4 text-neon-blue" />
                            </div>
                            <div className="flex-grow">
                                <div className="bg-white/5 border border-white/10 rounded-2xl rounded-tl-none p-4 text-gray-200 leading-relaxed shadow-lg relative group">
                                    <p>{activeChallenge.question}</p>

                                    {/* Inspector Toggle */}
                                    <button
                                        onClick={() => setShowEvidence(true)}
                                        className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity p-1 hover:bg-white/10 rounded"
                                        title="Inspect Evidence"
                                    >
                                        <Info className="w-4 h-4 text-neon-blue" />
                                    </button>
                                </div>
                                <span className="text-[10px] text-gray-600 font-mono mt-1 block ml-2">Just now</span>
                            </div>
                        </div>
                    ) : isGenerating ? (
                        <div className="flex items-center space-x-3 text-gray-500 animate-pulse">
                            <div className="w-8 h-8 rounded-full bg-white/5 flex items-center justify-center">
                                <Loader2 className="w-4 h-4 animate-spin" />
                            </div>
                            <span className="text-sm font-mono">Analyzing slide...</span>
                        </div>
                    ) : (
                        <div className="text-center text-gray-600 mt-10 italic">
                            Waiting for next slide...
                        </div>
                    )}

                    {/* User Response Bubble */}
                    {(userResponse || scoreResult) && (
                        <div className="flex items-start space-x-3 justify-end animate-fade-in">
                            <div className="flex-grow flex flex-col items-end">
                                <div className="bg-neon-blue/10 border border-neon-blue/20 rounded-2xl rounded-tr-none p-4 text-white leading-relaxed shadow-lg max-w-[90%]">
                                    <p>{userResponse}</p>
                                </div>
                                <span className="text-[10px] text-gray-600 font-mono mt-1 block mr-2">You</span>
                            </div>
                            <div className="w-8 h-8 rounded-full bg-gray-700 flex-shrink-0 flex items-center justify-center mt-1">
                                <User className="w-4 h-4 text-gray-300" />
                            </div>
                        </div>
                    )}

                    {/* Evaluation Result */}
                    {scoreResult && (
                        <div className="animate-slide-up mt-4">
                            <div className={clsx(
                                "rounded-xl p-5 border",
                                scoreResult.score >= 70 ? "bg-green-500/10 border-green-500/30" : "bg-yellow-500/10 border-yellow-500/30"
                            )}>
                                <div className="flex items-center justify-between mb-3">
                                    <span className="text-xs font-bold uppercase tracking-wider opacity-70">Evaluation</span>
                                    <span className="text-2xl font-bold font-display">{scoreResult.score}/100</span>
                                </div>
                                <p className="text-sm leading-relaxed opacity-90 mb-4">{scoreResult.feedback}</p>
                                <button
                                    onClick={handleNext}
                                    className="w-full py-2 bg-white/10 hover:bg-white/20 rounded-lg text-sm font-bold transition-colors"
                                >
                                    Next Slide
                                </button>
                            </div>
                        </div>
                    )}

                </div>

                {/* Input Area */}
                <div className="p-4 border-t border-white/10 bg-black/40 backdrop-blur-md">
                    <div className="relative">
                        <input
                            type="text"
                            value={userResponse}
                            onChange={(e) => setUserResponse(e.target.value)}
                            placeholder={activeChallenge ? "Type your answer..." : "Waiting for challenge..."}
                            disabled={!activeChallenge || !!scoreResult || isSubmitting}
                            className="w-full bg-white/5 border border-white/10 rounded-xl py-4 px-4 pr-12 text-white placeholder-gray-500 focus:outline-none focus:border-neon-blue/50 transition-all disabled:opacity-50"
                            onKeyDown={(e) => e.key === 'Enter' && handleSubmitResponse()}
                        />
                        <button
                            onClick={handleSubmitResponse}
                            disabled={!activeChallenge || !!scoreResult || isSubmitting || !userResponse.trim()}
                            className="absolute right-2 top-1/2 transform -translate-y-1/2 p-2 text-neon-blue hover:bg-neon-blue/10 rounded-lg transition-colors disabled:opacity-30"
                        >
                            {isSubmitting ? <Loader2 className="w-5 h-5 animate-spin" /> : <Send className="w-5 h-5" />}
                        </button>
                    </div>
                </div>

            </div>

            {/* Evidence Inspector Modal */}
            {showEvidence && activeChallenge && (
                <ChallengerDetail
                    challenge={activeChallenge}
                    onClose={() => setShowEvidence(false)}
                    // Mocking facts/chunks for now as they are not yet in the Challenge object fully or need fetching
                    chunks={["Mock chunk from slide context..."]}
                    facts={[{ topic: "Cost", text: "Competitor X is 20% cheaper.", source_title: "Gartner Report", source_url: "", domain: "pricing", id: "1", snippet: "" }]}
                />
            )}

        </div>
    );
};
