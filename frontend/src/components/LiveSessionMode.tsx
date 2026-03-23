import React, { useEffect, useState } from 'react';
import { AudioCapture } from './AudioCapture';
import { liveClient, SessionState, AgentState } from '../api/live';
import { User, Hand, MessageSquare } from 'lucide-react';
import { DGCard, DGButton, DGBadge } from './ui';

interface LiveSessionModeProps {
    sessionId: string;
    selectedPersonaIds: string[];
    onExit: () => void;
}

export const LiveSessionMode: React.FC<LiveSessionModeProps> = ({ sessionId, selectedPersonaIds, onExit }) => {
    const [sessionState, setSessionState] = useState<SessionState>({
        transcript_length: 0,
        agents: selectedPersonaIds.map(id => ({ persona_id: id, status: 'listening' }))
    });

    const [transcriptHistory, setTranscriptHistory] = useState<string[]>([]);

    useEffect(() => {
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
        setTranscriptHistory(prev => [...prev.slice(-4), text]);
    };

    return (
        <div className="flex flex-col h-full max-w-6xl mx-auto w-full gap-6">
            <header className="flex justify-between items-center pb-4 border-b border-slate-200">
                <div>
                    <div className="flex items-center gap-3 mb-1">
                        <h1 className="text-2xl font-bold text-slate-900">
                            Live Gauntlet
                        </h1>
                        <DGBadge variant="warning">Beta — Chrome only</DGBadge>
                    </div>
                    <p className="text-slate-500 text-sm">Present your deck. Agents will raise their hand if they have questions.</p>
                </div>
                <DGButton variant="secondary" size="sm" onClick={onExit}>
                    End Session
                </DGButton>
            </header>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 flex-1">
                {/* Presenter Area */}
                <div className="lg:col-span-2 flex flex-col gap-4">
                    <DGCard variant="elevated" className="flex-1 p-6 flex flex-col items-center justify-center min-h-[300px]">
                        <div className="flex flex-col items-center gap-6 w-full max-w-md">
                            <AudioCapture onTranscript={handleTranscript} />

                            <div className="w-full space-y-2 mt-4">
                                <p className="text-xs text-slate-400 font-mono text-center mb-2">LIVE TRANSCRIPT</p>
                                {transcriptHistory.map((t, i) => (
                                    <p key={i} className="text-slate-600 text-sm text-center animate-in fade-in slide-in-from-bottom-2">
                                        "{t}"
                                    </p>
                                ))}
                                {transcriptHistory.length === 0 && (
                                    <p className="text-slate-400 text-sm text-center italic">
                                        (Words will appear here...)
                                    </p>
                                )}
                            </div>
                        </div>
                    </DGCard>
                </div>

                {/* Agent Gallery */}
                <DGCard variant="elevated" className="flex flex-col gap-4 p-4">
                    <h2 className="text-lg font-semibold text-slate-900 flex items-center gap-2">
                        <User className="w-5 h-5 text-slate-500" />
                        Audience
                    </h2>

                    <div className="flex flex-col gap-3 overflow-y-auto max-h-[600px] pr-2">
                        {sessionState.agents.map(agent => (
                            <AgentCard key={agent.persona_id} agent={agent} />
                        ))}
                    </div>
                </DGCard>
            </div>
        </div>
    );
};

const AgentCard: React.FC<{ agent: AgentState }> = ({ agent }) => {
    const isRaised = agent.status === 'raising_hand';
    const isThinking = agent.status === 'thinking';

    // Convert persona_id to display name
    const displayName = agent.persona_id
        .split('_')
        .map(w => w.charAt(0).toUpperCase() + w.slice(1))
        .join(' ');

    return (
        <DGCard
            className={[
                'p-4 transition-all duration-300',
                isRaised ? 'border-amber-300 bg-amber-50 shadow-sm' : 'border-slate-200',
            ].join(' ')}
        >
            <div className="flex items-start justify-between">
                <div>
                    <h3 className="font-semibold text-slate-900">
                        {displayName}
                    </h3>
                    <span className="text-xs text-slate-500 uppercase tracking-wider">
                        {agent.status.replace(/_/g, ' ')}
                    </span>
                </div>

                {isRaised && (
                    <div className="animate-bounce bg-amber-500 text-white p-1.5 rounded-full">
                        <Hand className="w-5 h-5" />
                    </div>
                )}
                {isThinking && (
                    <div className="w-2 h-2 rounded-full bg-slate-400 animate-pulse" />
                )}
            </div>

            {agent.message && (
                <div className={[
                    'mt-3 text-sm p-3 rounded-lg border',
                    isRaised
                        ? 'bg-amber-50 border-amber-200 text-amber-900'
                        : 'bg-slate-50 border-slate-200 text-slate-600',
                ].join(' ')}>
                    <div className="flex gap-2">
                        <MessageSquare className="w-4 h-4 mt-0.5 shrink-0 opacity-70" />
                        <p>{agent.message}</p>
                    </div>
                </div>
            )}
        </DGCard>
    );
};
