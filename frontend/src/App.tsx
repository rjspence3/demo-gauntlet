import React, { useState } from 'react';
import { UploadView } from './components/UploadView';
import { ResearchView } from './components/ResearchView';
import { ChallengerSelection } from './components/ChallengerSelection';
import { DemoRoom } from './components/DemoRoom';
import { SummaryView } from './components/SummaryView';
import { LayoutGrid, FileText, Swords, BarChart, Zap, Users } from 'lucide-react';
import { clsx } from 'clsx';

type View = 'upload' | 'research' | 'selection' | 'challenge' | 'summary';

function App() {
    const [view, setView] = useState<View>('upload');
    const [sessionId, setSessionId] = useState<string | null>(null);
    const [selectedPersonaIds, setSelectedPersonaIds] = useState<string[]>([]);

    const handleUploadComplete = (sid: string) => {
        setSessionId(sid);
        setView('research');
    };

    const handleResearchComplete = () => {
        setView('selection');
    };

    const handleChallengersUpdated = (personaIds: string[]) => {
        setSelectedPersonaIds(personaIds);
    };

    const handleStartSimulation = () => {
        if (selectedPersonaIds.length > 0) {
            setView('challenge');
        }
    };

    return (
        <div className="min-h-screen text-white font-sans selection:bg-neon-blue/30 selection:text-neon-blue">
            {/* Navigation / Header */}
            <nav className="fixed top-0 left-0 right-0 z-50 border-b border-white/10 bg-cyber-black/80 backdrop-blur-md">
                <div className="max-w-7xl mx-auto px-6 h-20 flex items-center justify-between">
                    <div className="flex items-center space-x-3 group cursor-pointer" onClick={() => setView('upload')}>
                        <div className="relative">
                            <div className="absolute inset-0 bg-neon-blue blur-md opacity-20 group-hover:opacity-50 transition-opacity"></div>
                            <Swords className="w-8 h-8 text-neon-blue relative z-10" />
                        </div>
                        <span className="font-display font-bold text-2xl tracking-tight bg-gradient-to-r from-white to-gray-400 bg-clip-text text-transparent">
                            Demo Gauntlet
                        </span>
                    </div>

                    {sessionId && (
                        <div className="flex items-center space-x-2 bg-white/5 rounded-full p-1.5 border border-white/10 backdrop-blur-sm">
                            <button
                                onClick={() => setView('upload')}
                                className={clsx(
                                    "px-4 py-2 rounded-full text-sm font-medium transition-all duration-300",
                                    view === 'upload'
                                        ? "bg-neon-blue/20 text-neon-blue shadow-[0_0_10px_rgba(0,243,255,0.2)] border border-neon-blue/30"
                                        : "text-gray-400 hover:text-white hover:bg-white/5"
                                )}
                            >
                                Upload
                            </button>
                            <button
                                onClick={() => setView('research')}
                                className={clsx(
                                    "px-4 py-2 rounded-full text-sm font-medium transition-all duration-300",
                                    view === 'research'
                                        ? "bg-neon-purple/20 text-neon-purple shadow-[0_0_10px_rgba(188,19,254,0.2)] border border-neon-purple/30"
                                        : "text-gray-400 hover:text-white hover:bg-white/5"
                                )}
                            >
                                Research
                            </button>
                            <button
                                onClick={() => setView('selection')}
                                disabled={!sessionId}
                                className={clsx(
                                    "p-2 rounded-full transition-all duration-300",
                                    view === 'selection'
                                        ? "bg-white/20 text-white shadow-[0_0_10px_rgba(255,255,255,0.2)] border border-white/30"
                                        : "hover:bg-white/5 text-gray-400 disabled:opacity-30"
                                )}
                            >
                                <Users className="w-5 h-5" />
                            </button>
                            <button
                                onClick={() => setView('challenge')}
                                disabled={!sessionId || selectedPersonaIds.length === 0}
                                className={clsx(
                                    "p-2 rounded-full transition-all duration-300",
                                    view === 'challenge'
                                        ? "bg-danger-red/20 text-danger-red shadow-[0_0_10px_rgba(255,0,60,0.2)] border border-danger-red/30"
                                        : "hover:bg-white/5 text-gray-400 disabled:opacity-30"
                                )}
                            >
                                <Zap className="w-5 h-5" />
                            </button>
                            <button
                                onClick={() => setView('summary')}
                                disabled={!sessionId}
                                className={clsx(
                                    "p-2 rounded-full transition-all duration-300",
                                    view === 'summary'
                                        ? "bg-neon-pink/20 text-neon-pink shadow-[0_0_10px_rgba(255,0,255,0.2)] border border-neon-pink/30"
                                        : "hover:bg-white/5 text-gray-400 disabled:opacity-30"
                                )}
                            >
                                <BarChart className="w-5 h-5" />
                            </button>
                        </div>
                    )}
                </div>
            </nav>

            {/* Main Content */}
            <main className="container mx-auto px-4 pt-32 pb-12 relative z-10">
                {view === 'upload' && (
                    <UploadView onUploadComplete={handleUploadComplete} />
                )}

                {view === 'research' && sessionId && (
                    <ResearchView
                        sessionId={sessionId}
                        onResearchComplete={handleResearchComplete}
                    />
                )}

                {view === 'selection' && sessionId && (
                    <ChallengerSelection
                        sessionId={sessionId}
                        onSelectionChanged={handleChallengersUpdated}
                        onConfirm={handleStartSimulation}
                    />
                )}

                {view === 'challenge' && sessionId && (
                    <DemoRoom
                        sessionId={sessionId}
                        selectedPersonaIds={selectedPersonaIds}
                        onFinish={() => setView('summary')}
                    />
                )}

                {view === 'summary' && sessionId && (
                    <SummaryView sessionId={sessionId} onRestart={() => setView('upload')} />
                )}
            </main>

            {/* Background Grid Effect */}
            <div className="fixed inset-0 z-0 pointer-events-none"
                style={{
                    backgroundImage: 'linear-gradient(rgba(255, 255, 255, 0.03) 1px, transparent 1px), linear-gradient(90deg, rgba(255, 255, 255, 0.03) 1px, transparent 1px)',
                    backgroundSize: '50px 50px',
                    maskImage: 'radial-gradient(circle at center, black, transparent 80%)'
                }}>
            </div>
        </div>
    );
}

export default App;
