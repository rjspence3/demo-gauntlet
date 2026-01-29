import React, { useEffect, useState } from 'react';
import { AudioCapture } from './AudioCapture';
import { liveClient, SessionState, AgentState } from '../api/live';
import { User, Hand, MessageSquare } from 'lucide-react';

interface LiveSessionModeProps {
    sessionId: string;
    selectedPersonaIds: string[];
    onExit: () => void;
}

export const LiveSessionMode: React.FC<LiveSessionModeProps> = ({ sessionId, selectedPersonaIds, onExit }) => {
    const [sessionState, setSessionState] = useState<SessionState>({
        transcript_length: 0,
        agents: selectedPersonaIds.map(id => ({ persona_id: id, status: 'listening' })) // Initial optimistic state
    });

    const [transcriptHistory, setTranscriptHistory] = useState<string[]>([]);

    useEffect(() => {
        // Connect and Init
        liveClient.connect();
        liveClient.initSession(sessionId, selectedPersonaIds);

        const unsubscribe = liveClient.subscribe((event) => {
            if (event.type === 'state_update') {
                setSessionState(event.data);
            }
        });

        return () => {
            unsubscribe();
            liveClient.disconnect();
        };
    }, [selectedPersonaIds]);

    const handleTranscript = (text: string) => {
        setTranscriptHistory(prev => [...prev.slice(-4), text]); // Keep last 5 chunks for UI
    };

    return (
        <div className="flex flex-col h-full max-w-6xl mx-auto w-full gap-6">
            <header className="flex justify-between items-center pb-4 border-b border-slate-800">
                <div>
                    <h1 className="text-2xl font-bold bg-gradient-to-r from-cyan-400 to-blue-500 bg-clip-text text-transparent">
                        Live Gauntlet
                    </h1>
                    <p className="text-slate-400 text-sm">Present your deck. Agents will raise their hand if they have questions.</p>
                </div>
                <button
                    onClick={onExit}
                    className="px-4 py-2 rounded-md bg-slate-800 hover:bg-slate-700 text-slate-300 transition-colors"
                >
                    End Session
                </button>
            </header>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 flex-1">
                {/* Presenter Area (Left/Top) */}
                <div className="lg:col-span-2 flex flex-col gap-4">
                    <div className="flex-1 bg-slate-900/50 rounded-xl border border-slate-800 p-6 flex flex-col items-center justify-center min-h-[300px] relative overflow-hidden group">
                        <div className="absolute inset-0 bg-gradient-to-br from-cyan-500/5 to-purple-500/5 pointer-events-none" />

                        <div className="z-10 flex flex-col items-center gap-6 w-full max-w-md">
                            <AudioCapture onTranscript={handleTranscript} />

                            <div className="w-full space-y-2 mt-4">
                                <p className="text-xs text-slate-500 font-mono text-center mb-2">LIVE TRANSCRIPT</p>
                                {transcriptHistory.map((t, i) => (
                                    <p key={i} className="text-slate-400 text-sm text-center animate-in fade-in slide-in-from-bottom-2">
                                        "{t}"
                                    </p>
                                ))}
                                {transcriptHistory.length === 0 && (
                                    <p className="text-slate-600 text-sm text-center italic">
                                        (Words will appear here...)
                                    </p>
                                )}
                            </div>
                        </div>
                    </div>
                </div>

                {/* Agent Gallery (Right/Bottom) */}
                <div className="flex flex-col gap-4 bg-slate-900/30 rounded-xl border border-slate-800 p-4">
                    <h2 className="text-lg font-semibold text-slate-300 flex items-center gap-2">
                        <User className="w-5 h-5" />
                        Audience
                    </h2>

                    <div className="flex flex-col gap-3 overflow-y-auto max-h-[600px] pr-2">
                        {sessionState.agents.map(agent => (
                            <AgentCard key={agent.persona_id} agent={agent} />
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
};

const AgentCard: React.FC<{ agent: AgentState }> = ({ agent }) => {
    // Determine color/style based on status
    const isRaised = agent.status === 'raising_hand';
    const isThinking = agent.status === 'thinking';

    return (
        <div className={`
            relative p-4 rounded-lg border transition-all duration-300
            ${isRaised
                ? 'bg-amber-500/10 border-amber-500/50 shadow-[0_0_15px_rgba(245,158,11,0.2)]'
                : 'bg-slate-800/50 border-slate-700 hover:border-slate-600'}
        `}>
            <div className="flex items-start justify-between">
                <div>
                    <h3 className="font-semibold text-slate-200 capitalize">
                        {agent.persona_id.replace('_', ' ')}
                    </h3>
                    <span className="text-xs text-slate-500 uppercase tracking-wider">
                        {agent.status.replace('_', ' ')}
                    </span>
                </div>

                {isRaised && (
                    <div className="animate-bounce bg-amber-500 text-slate-900 p-1.5 rounded-full">
                        <Hand className="w-5 h-5" />
                    </div>
                )}
            </div>

            {agent.message && (
                <div className={`
                    mt-3 text-sm p-3 rounded-md border
                    ${isRaised
                        ? 'bg-amber-950/30 border-amber-900/50 text-amber-100'
                        : 'bg-slate-900/50 border-slate-800 text-slate-400'}
                `}>
                    <div className="flex gap-2">
                        <MessageSquare className="w-4 h-4 mt-0.5 shrink-0 opacity-70" />
                        <p>{agent.message}</p>
                    </div>
                </div>
            )}
        </div>
    );
}
