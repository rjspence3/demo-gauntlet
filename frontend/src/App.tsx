import React, { useState, useEffect } from 'react';
import { DeckUpload } from './components/DeckUpload';
import { ProcessingScreen, ProcessingStep } from './components/ProcessingScreen';
import { ChallengerSelection, Challenger } from './components/ChallengerSelection';
import { liveClient } from './api/live'; // Ensure client is initialized
import { LiveSessionMode } from './components/LiveSessionMode';
import { DemoRoom } from './components/DemoRoom';
import { SummaryView } from './components/SummaryView';
import { uploadDeck, getSessionStatus, generateResearch, listPersonas, precomputeChallenges } from './api/client';
import { Swords, BarChart, Zap, Users, Loader2, AlertCircle } from 'lucide-react';
import { DGLayoutShell, DGIconButton, DGCard } from './components/ui';

type View = 'upload' | 'research' | 'selection' | 'challenge' | 'live' | 'summary';

function App() {
    const [view, setView] = useState<View>('upload');
    const [sessionId, setSessionId] = useState<string | null>(() => {
        // Restore session on page refresh so the user doesn't lose progress
        return localStorage.getItem('dg_session_id');
    });
    const [selectedPersonaIds, setSelectedPersonaIds] = useState<string[]>([]);
    const [processingStep, setProcessingStep] = useState<ProcessingStep>('uploading');
    const [challengers, setChallengers] = useState<Challenger[]>([]);
    const [personasLoading, setPersonasLoading] = useState(true);
    const [personasError, setPersonasError] = useState(false);
    const [uploadError, setUploadError] = useState<string | null>(null);
    const [processingError, setProcessingError] = useState<string | null>(null);
    const [startError, setStartError] = useState<string | null>(null);

    // Load personas once on mount — no auth required
    useEffect(() => {
        const fetchPersonas = async () => {
            try {
                const personas = await listPersonas();
                const uiPersonas = personas.map(p => ({
                    ...p,
                    description: p.style,
                }));
                setChallengers(uiPersonas);
            } catch (err) {
                console.error("Failed to fetch personas:", err);
                setPersonasError(true);
            } finally {
                setPersonasLoading(false);
            }
        };
        fetchPersonas();
    }, []);

    // Processing Logic
    useEffect(() => {
        if (view !== 'research' || !sessionId) return;

        setProcessingStep('uploading');
        setProcessingError(null);
        let stopped = false;

        const run = async () => {
            // Step 1: Poll until ingestion is complete
            while (!stopped) {
                await new Promise(r => setTimeout(r, 2000));
                if (stopped) return;
                try {
                    const statusRes = await getSessionStatus(sessionId);
                    if (statusRes.status === 'completed') break;
                    if (statusRes.status === 'failed') {
                        setProcessingError("Processing failed. Please try uploading again.");
                        setView('upload');
                        return;
                    }
                } catch (e) {
                    console.error("Polling error", e);
                }
            }
            if (stopped) return;

            // Step 2: Run research generation (visible step)
            setProcessingStep('researching');
            try {
                await generateResearch(sessionId);
            } catch (err) {
                console.warn("Research generation failed, continuing without dossier:", err);
            }
            if (stopped) return;

            // Step 3: Done
            setProcessingStep('complete');
            setTimeout(() => setView('selection'), 1000);
        };

        run();
        return () => { stopped = true; };
    }, [view, sessionId]);

    const handleNewSession = () => {
        localStorage.removeItem('dg_session_id');
        setSessionId(null);
        setSelectedPersonaIds([]);
        setUploadError(null);
        setProcessingError(null);
        setStartError(null);
        setView('upload');
    };

    const handleUploadComplete = async (file: File) => {
        try {
            setUploadError(null);
            setProcessingStep('uploading');
            const res = await uploadDeck(file);
            localStorage.setItem('dg_session_id', res.session_id);
            setSessionId(res.session_id);
            setView('research');
        } catch (err) {
            console.error("Upload failed", err);
            setUploadError("Upload failed. Please check your connection and try again.");
        }
    };

    const handleStartSimulation = async (selectedIds: string[]) => {
        try {
            setStartError(null);
            if (!sessionId) return;
            await precomputeChallenges(sessionId, selectedIds);
            setSelectedPersonaIds(selectedIds);
            setView('challenge');
        } catch (err) {
            console.error("Failed to start simulation:", err);
            setStartError("Failed to generate challenges. Please try again.");
        }
    };

    if (personasLoading) {
        return (
            <DGLayoutShell>
                <div className="min-h-screen flex items-center justify-center">
                    <div className="flex flex-col items-center gap-4">
                        <Loader2 className="w-10 h-10 text-orange-500 animate-spin" />
                        <p className="text-slate-400 text-sm font-mono animate-pulse">Initializing...</p>
                    </div>
                </div>
            </DGLayoutShell>
        );
    }

    return (
        <DGLayoutShell>
            {/* Navigation / Header */}
            <nav className="fixed top-0 left-0 right-0 z-50 border-b border-slate-200 bg-white/90 backdrop-blur-md">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 h-16 sm:h-20 flex items-center justify-between">
                    <button
                        className="flex items-center space-x-2 sm:space-x-3 group"
                        onClick={handleNewSession}
                    >
                        <Swords className="w-6 sm:w-8 h-6 sm:h-8 text-orange-500" />
                        <span className="font-bold text-xl sm:text-2xl tracking-tight text-slate-900">
                            Demo <span className="text-orange-500">Gauntlet</span>
                        </span>
                    </button>

                    <div className="flex items-center space-x-2 sm:space-x-4">
                        {sessionId && (
                            <div className="flex items-center space-x-1 sm:space-x-2 bg-slate-50 rounded-full p-1 sm:p-1.5 border border-slate-200">
                                <DGIconButton
                                    icon={<Users className="w-4 sm:w-5 h-4 sm:h-5" />}
                                    ariaLabel="Challenger selection"
                                    tooltip="Challengers"
                                    size="sm"
                                    variant={view === 'selection' ? 'active' : 'default'}
                                    disabled={!sessionId}
                                    onClick={() => setView('selection')}
                                />
                                <DGIconButton
                                    icon={<Zap className="w-4 sm:w-5 h-4 sm:h-5" />}
                                    ariaLabel="Demo room"
                                    tooltip="Simulation"
                                    size="sm"
                                    variant={view === 'challenge' ? 'active' : 'default'}
                                    disabled={!sessionId || selectedPersonaIds.length === 0}
                                    onClick={() => setView('challenge')}
                                />
                                <DGIconButton
                                    icon={<Swords className="w-4 sm:w-5 h-4 sm:h-5" />}
                                    ariaLabel="Live Session"
                                    tooltip="Live Mode"
                                    size="sm"
                                    variant={view === 'live' ? 'active' : 'default'}
                                    disabled={!sessionId || selectedPersonaIds.length === 0}
                                    onClick={() => setView('live')}
                                />
                                <DGIconButton
                                    icon={<BarChart className="w-4 sm:w-5 h-4 sm:h-5" />}
                                    ariaLabel="Summary report"
                                    tooltip="Summary"
                                    size="sm"
                                    variant={view === 'summary' ? 'active' : 'default'}
                                    disabled={!sessionId}
                                    onClick={() => setView('summary')}
                                />
                            </div>
                        )}

                        <DGIconButton
                            icon={<Swords className="w-4 sm:w-5 h-4 sm:h-5 rotate-180" />}
                            ariaLabel="New session"
                            tooltip="New Session"
                            size="sm"
                            onClick={handleNewSession}
                        />
                    </div>
                </div>
            </nav>

            {/* Main Content */}
            <main className="container mx-auto px-4 pt-24 sm:pt-32 pb-12 relative z-10">
                {/* Error banners */}
                {uploadError && (
                    <DGCard className="mb-4 max-w-2xl mx-auto p-4 border-rose-200 bg-rose-50">
                        <div className="flex items-center gap-3 text-rose-700 text-sm">
                            <AlertCircle className="w-5 h-5 flex-shrink-0" />
                            {uploadError}
                        </div>
                    </DGCard>
                )}
                {processingError && (
                    <DGCard className="mb-4 max-w-2xl mx-auto p-4 border-rose-200 bg-rose-50">
                        <div className="flex items-center gap-3 text-rose-700 text-sm">
                            <AlertCircle className="w-5 h-5 flex-shrink-0" />
                            {processingError}
                        </div>
                    </DGCard>
                )}
                {startError && (
                    <DGCard className="mb-4 max-w-2xl mx-auto p-4 border-rose-200 bg-rose-50">
                        <div className="flex items-center gap-3 text-rose-700 text-sm">
                            <AlertCircle className="w-5 h-5 flex-shrink-0" />
                            {startError}
                        </div>
                    </DGCard>
                )}

                {view === 'upload' && (
                    <DeckUpload onUploadComplete={handleUploadComplete} />
                )}

                {view === 'research' && (
                    <ProcessingScreen currentStep={processingStep} />
                )}

                {view === 'selection' && (
                    <ChallengerSelection
                        challengers={challengers}
                        onStartSimulation={handleStartSimulation}
                        loadError={personasError}
                    />
                )}

                {view === 'challenge' && sessionId && (
                    <DemoRoom
                        sessionId={sessionId}
                        selectedPersonaIds={selectedPersonaIds}
                        onFinish={() => setView('summary')}
                    />
                )}

                {view === 'live' && sessionId && (
                    <LiveSessionMode
                        sessionId={sessionId}
                        selectedPersonaIds={selectedPersonaIds}
                        onExit={() => setView('summary')}
                    />
                )}

                {view === 'summary' && sessionId && (
                    <SummaryView sessionId={sessionId} onRestart={handleNewSession} />
                )}
            </main>

            <footer className="border-t border-slate-200 bg-white py-4 px-6 text-center">
                <p className="text-xs text-slate-400">
                    Demo Gauntlet &middot; Built by{" "}
                    <a
                        href="https://nomouthlabs.com"
                        className="underline hover:text-slate-600 transition-colors"
                    >
                        Rob Spence
                    </a>
                    {" "}&middot; nomouthlabs.com
                </p>
            </footer>
        </DGLayoutShell>
    );
}

export default App;
