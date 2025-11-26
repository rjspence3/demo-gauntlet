import React, { useState } from 'react';
import { UploadView } from './components/UploadView';
import { ResearchView } from './components/ResearchView';
import { DemoRoom } from './components/DemoRoom';
import { SummaryView } from './components/SummaryView';
import { LayoutGrid, FileText, Swords, BarChart } from 'lucide-react';
import { clsx } from 'clsx';

type View = 'upload' | 'research' | 'challenge' | 'summary';

function App() {
    const [view, setView] = useState<View>('upload');
    const [sessionId, setSessionId] = useState<string | null>(null);

    const handleUploadComplete = (sid: string) => {
        setSessionId(sid);
        setView('research');
    };

    const handleResearchComplete = () => {
        setView('challenge');
    };

    return (
        <div className="min-h-screen bg-[#1a1a1a] text-white font-sans selection:bg-blue-500/30">
            {/* Navigation / Header */}
            <nav className="border-b border-gray-800 bg-gray-900/50 backdrop-blur-md sticky top-0 z-50">
                <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                        <Swords className="w-6 h-6 text-blue-500" />
                        <span className="font-bold text-xl tracking-tight">Demo Gauntlet</span>
                    </div>

                    {sessionId && (
                        <div className="flex items-center space-x-1 bg-gray-800 rounded-full p-1">
                            <button
                                onClick={() => setView('upload')}
                                className={clsx(
                                    "px-4 py-1.5 rounded-full text-sm font-medium transition-all",
                                    view === 'upload' ? "bg-gray-700 text-white shadow-sm" : "text-gray-400 hover:text-gray-200"
                                )}
                            >
                                Upload
                            </button>
                            <button
                                onClick={() => setView('research')}
                                className={clsx(
                                    "px-4 py-1.5 rounded-full text-sm font-medium transition-all",
                                    view === 'research' ? "bg-blue-600 text-white shadow-sm" : "text-gray-400 hover:text-gray-200"
                                )}
                            >
                                Research
                            </button>
                            <button
                                onClick={() => setView('challenge')}
                                disabled={!sessionId}
                                className={clsx("p-2 rounded transition-colors", view === 'challenge' ? "bg-gray-800 text-blue-400" : "hover:bg-gray-800 text-gray-400 disabled:opacity-30")}
                            >
                                <Swords className="w-6 h-6" />
                            </button>
                            <button
                                onClick={() => setView('summary')}
                                disabled={!sessionId}
                                className={clsx("p-2 rounded transition-colors", view === 'summary' ? "bg-gray-800 text-blue-400" : "hover:bg-gray-800 text-gray-400 disabled:opacity-30")}
                            >
                                <BarChart className="w-6 h-6" />
                            </button>
                        </div>
                    )}
                </div>
            </nav>

            {/* Main Content */}
            <main className="container mx-auto px-4 py-8">
                {view === 'upload' && (
                    <UploadView onUploadComplete={handleUploadComplete} />
                )}

                {view === 'research' && sessionId && (
                    <ResearchView
                        sessionId={sessionId}
                        onResearchComplete={handleResearchComplete}
                    />
                )}

                {view === 'challenge' && sessionId && (
                    <DemoRoom sessionId={sessionId} onFinish={() => setView('summary')} />
                )}

                {view === 'summary' && sessionId && (
                    <SummaryView sessionId={sessionId} onRestart={() => setView('upload')} />
                )}
            </main>
        </div>
    );
}

export default App;
