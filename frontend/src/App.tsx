import React, { useState, useEffect } from 'react';
import { DeckUpload } from './components/DeckUpload';
import { ProcessingScreen, ProcessingStep } from './components/ProcessingScreen';
import { ChallengerSelection, Challenger } from './components/ChallengerSelection';
import { liveClient } from './api/live';
import { LiveSessionMode } from './components/LiveSessionMode';
import { DemoRoom } from './components/DemoRoom';
import { SummaryView } from './components/SummaryView';
import { uploadDeck, getSessionStatus, generateResearch, listPersonas, precomputeChallenges } from './api/client';
import { Swords, BarChart, Zap, Users, Loader2, AlertCircle } from 'lucide-react';
import { DGLayoutShell, DGIconButton } from './components/ui';

type View = 'upload' | 'research' | 'selection' | 'challenge' | 'live' | 'summary';

function App() {
    const [view, setView] = useState<View>('upload');
    const [sessionId, setSessionId] = useState<string | null>(() => {
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

    useEffect(() => {
        const fetchPersonas = async () => {
            try {
                const personas = await listPersonas();
                const uiPersonas = personas.map(p => ({
                    ...p,
                    description: p.style,
                    tags: p.focus_areas ?? [],
                    evidenceCount: 0,
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

    useEffect(() => {
        if (view !== 'research' || !sessionId) return;

        setProcessingStep('uploading');
        setProcessingError(null);
        let stopped = false;

        const run = async () => {
            const pollDeadline = Date.now() + 2 * 60 * 1000;
            while (!stopped) {
                await new Promise(r => setTimeout(r, 2000));
                if (stopped) return;
                if (Date.now() > pollDeadline) {
                    setProcessingError("Processing timed out. Please try again.");
                    setView('upload');
                    return;
                }
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

            setProcessingStep('researching');
            try {
                await generateResearch(sessionId);
            } catch (err) {
                console.warn("Research generation failed, continuing without dossier:", err);
            }
            if (stopped) return;

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
                    <div className="flex flex-col items-center gap-3">
                        <Loader2 className="w-6 h-6 text-brand-500 animate-spin" />
                        <p className="text-text-faint text-xs font-mono animate-pulse">Initializing...</p>
                    </div>
                </div>
            </DGLayoutShell>
        );
    }

    const errorBanner = (message: string) => (
        <div className="mb-4 max-w-2xl mx-auto rounded-lg border border-status-error/20 bg-status-error/5 px-4 py-3">
            <div className="flex items-center gap-2.5 text-status-error text-sm">
                <AlertCircle className="w-4 h-4 flex-shrink-0" />
                {message}
            </div>
        </div>
    );

    return (
        <DGLayoutShell>
            {/* Navigation */}
            <nav className="fixed top-0 left-0 right-0 z-50 border-b border-border bg-white/90 backdrop-blur-md">
                <div className="max-w-6xl mx-auto px-4 sm:px-6 h-14 flex items-center justify-between">
                    <button
                        className="flex items-center gap-2 group"
                        onClick={handleNewSession}
                    >
                        <Swords className="w-5 h-5 text-brand-500" />
                        <span className="font-semibold text-sm text-text-primary">
                            Demo <span className="text-brand-500">Gauntlet</span>
                        </span>
                    </button>

                    <div className="flex items-center gap-1">
                        {sessionId && (
                            <div className="flex items-center gap-0.5 bg-surface-elevated rounded-lg p-0.5 border border-border mr-2">
                                <DGIconButton
                                    icon={<Users className="w-4 h-4" />}
                                    ariaLabel="Challenger selection"
                                    tooltip="Challengers"
                                    size="sm"
                                    variant={view === 'selection' ? 'active' : 'default'}
                                    disabled={!sessionId}
                                    onClick={() => setView('selection')}
                                />
                                <DGIconButton
                                    icon={<Zap className="w-4 h-4" />}
                                    ariaLabel="Demo room"
                                    tooltip="Simulation"
                                    size="sm"
                                    variant={view === 'challenge' ? 'active' : 'default'}
                                    disabled={!sessionId || selectedPersonaIds.length === 0}
                                    onClick={() => setView('challenge')}
                                />
                                <DGIconButton
                                    icon={<Swords className="w-4 h-4" />}
                                    ariaLabel="Live Session"
                                    tooltip="Live Mode"
                                    size="sm"
                                    variant={view === 'live' ? 'active' : 'default'}
                                    disabled={!sessionId || selectedPersonaIds.length === 0}
                                    onClick={() => setView('live')}
                                />
                                <DGIconButton
                                    icon={<BarChart className="w-4 h-4" />}
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
                            icon={<Swords className="w-4 h-4 rotate-180" />}
                            ariaLabel="New session"
                            tooltip="New Session"
                            size="sm"
                            onClick={handleNewSession}
                        />
                    </div>
                </div>
            </nav>

            {/* Main Content */}
            <main className="container mx-auto px-4 pt-20 pb-12 relative z-10 flex-1">
                {uploadError && errorBanner(uploadError)}
                {processingError && errorBanner(processingError)}
                {startError && errorBanner(startError)}

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

            <footer className="border-t border-border py-4 px-6 text-center">
                <p className="text-xs text-text-faint">
                    Demo Gauntlet &middot; Built by{" "}
                    <a
                        href="https://nomouthlabs.com"
                        className="text-text-muted hover:text-text-primary transition-colors"
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
