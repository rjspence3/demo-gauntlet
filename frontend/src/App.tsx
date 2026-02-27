import React, { useState, useEffect } from 'react';
import { DeckUpload } from './components/DeckUpload';
import { ProcessingScreen, ProcessingStep } from './components/ProcessingScreen';
import { ChallengerSelection, Challenger } from './components/ChallengerSelection';
import { liveClient } from './api/live'; // Ensure client is initialized
import { LiveSessionMode } from './components/LiveSessionMode';
import { DemoRoom } from './components/DemoRoom';
import { SummaryView } from './components/SummaryView';
import { AuthView } from './components/AuthView';
import { setAuthToken, uploadDeck, getSessionStatus, generateResearch, listPersonas, precomputeChallenges } from './api/client';
import { Swords, BarChart, Zap, Users, LogOut } from 'lucide-react';
import { cn } from './lib/utils';
import { DGLayoutShell, DGIconButton } from './components/ui';

type View = 'upload' | 'research' | 'selection' | 'challenge' | 'live' | 'summary';



function App() {
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    const [view, setView] = useState<View>('upload');
    const [sessionId, setSessionId] = useState<string | null>(null);
    const [selectedPersonaIds, setSelectedPersonaIds] = useState<string[]>([]);
    const [processingStep, setProcessingStep] = useState<ProcessingStep>('uploading');

    const [challengers, setChallengers] = useState<Challenger[]>([]);

    useEffect(() => {
        const token = localStorage.getItem('token');
        if (token) {
            setAuthToken(token);
            setIsAuthenticated(true);
        }
    }, []);

    // Fetch personas on load (or when auth changes)
    useEffect(() => {
        if (isAuthenticated) {
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
                }
            };
            fetchPersonas();
        }
    }, [isAuthenticated]);

    // Processing Logic
    useEffect(() => {
        if (view !== 'research' || !sessionId) return;

        setProcessingStep('uploading');
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
                        alert("Processing failed. Please try again.");
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

    const handleLoginSuccess = () => {
        setIsAuthenticated(true);
    };

    const handleLogout = () => {
        localStorage.removeItem('token');
        setAuthToken(null);
        setIsAuthenticated(false);
        setSessionId(null);
        setView('upload');
    };

    const handleUploadComplete = async (file: File) => {
        try {
            setProcessingStep('uploading');
            const res = await uploadDeck(file);
            setSessionId(res.session_id);
            setView('research');
        } catch (err) {
            console.error("Upload failed", err);
            alert("Upload failed. Please check console.");
        }
    };

    const handleStartSimulation = async (selectedIds: string[]) => {
        try {
            if (!sessionId) return;
            // Precompute challenges
            // We can show a loading state here too?
            await precomputeChallenges(sessionId, selectedIds);

            setSelectedPersonaIds(selectedIds);
            setView('challenge');
        } catch (err) {
            console.error("Failed to start simulation:", err);
            alert("Failed to generate challenges.");
        }
    };

    if (!isAuthenticated) {
        return <AuthView onAuthSuccess={handleLoginSuccess} />;
    }

    return (
        <DGLayoutShell>
            {/* Navigation / Header */}
            <nav className="fixed top-0 left-0 right-0 z-50 border-b border-slate-800 bg-slate-950/80 backdrop-blur-md">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 h-16 sm:h-20 flex items-center justify-between">
                    <button
                        className="flex items-center space-x-2 sm:space-x-3 group"
                        onClick={() => setView('upload')}
                    >
                        <div className="relative">
                            <div className="absolute inset-0 bg-cyan-400 blur-md opacity-20 group-hover:opacity-50 transition-opacity"></div>
                            <Swords className="w-6 sm:w-8 h-6 sm:h-8 text-cyan-400 relative z-10" />
                        </div>
                        <span className="font-bold text-xl sm:text-2xl tracking-tight bg-gradient-to-r from-white to-slate-400 bg-clip-text text-transparent">
                            Demo Gauntlet
                        </span>
                    </button>

                    <div className="flex items-center space-x-2 sm:space-x-4">
                        {sessionId && (
                            <div className="flex items-center space-x-1 sm:space-x-2 bg-slate-800/50 rounded-full p-1 sm:p-1.5 border border-slate-700 backdrop-blur-sm">
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
                            icon={<LogOut className="w-4 sm:w-5 h-4 sm:h-5" />}
                            ariaLabel="Logout"
                            tooltip="Logout"
                            size="sm"
                            onClick={handleLogout}
                        />
                    </div>
                </div>
            </nav>

            {/* Main Content */}
            <main className="container mx-auto px-4 pt-24 sm:pt-32 pb-12 relative z-10">
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
                    <SummaryView sessionId={sessionId} onRestart={() => setView('upload')} />
                )}
            </main>
        </DGLayoutShell>
    );
}

export default App;
