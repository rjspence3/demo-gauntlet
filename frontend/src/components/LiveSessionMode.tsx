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
        <div className="flex flex-col h-full max-w-5xl mx-auto w-full gap-4">
            <header className="flex justify-between items-center pb-4 border-b border-border">
                <div>
                    <div className="flex items-center gap-3 mb-1">
                        <h1 className="text-xl font-semibold text-text-primary">
                            Live Gauntlet
                        </h1>
                        <DGBadge variant="warning">Beta</DGBadge>
                    </div>
                    <p className="text-text-muted text-sm">Present your deck. Agents will raise their hand with questions.</p>
                </div>
                <DGButton variant="secondary" size="sm" onClick={onExit}>
                    End Session
                </DGButton>
            </header>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 flex-1">
                {/* Presenter Area */}
                <div className="lg:col-span-2 flex flex-col gap-4">
                    <DGCard className="flex-1 p-6 flex flex-col items-center justify-center min-h-[300px]">
                        <div className="flex flex-col items-center gap-6 w-full max-w-md">
                            <AudioCapture onTranscript={handleTranscript} />

                            <div className="w-full space-y-2 mt-4">
                                <p className="text-[10px] text-text-faint font-mono text-center mb-2 uppercase tracking-wider">Live Transcript</p>
                                {transcriptHistory.map((t, i) => (
                                    <p key={i} className="text-text-secondary text-sm text-center animate-fade-in">
                                        "{t}"
                                    </p>
                                ))}
                                {transcriptHistory.length === 0 && (
                                    <p className="text-text-faint text-sm text-center">
                                        Words will appear here...
                                    </p>
                                )}
                            </div>
                        </div>
                    </DGCard>
                </div>

                {/* Agent Gallery */}
                <DGCard className="flex flex-col gap-3 p-4">
                    <h2 className="text-sm font-semibold text-text-primary flex items-center gap-2">
                        <User className="w-4 h-4 text-text-muted" />
                        Audience
                    </h2>

                    <div className="flex flex-col gap-2 overflow-y-auto max-h-[600px]">
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

    const displayName = agent.persona_id
        .split('_')
        .map(w => w.charAt(0).toUpperCase() + w.slice(1))
        .join(' ');

    return (
        <div
            className={[
                'p-3 rounded-lg border transition-all duration-300',
                isRaised ? 'border-status-warning/30 bg-status-warning/5' : 'border-border bg-surface',
            ].join(' ')}
        >
            <div className="flex items-start justify-between">
                <div>
                    <h3 className="font-medium text-sm text-text-primary">
                        {displayName}
                    </h3>
                    <span className="text-[10px] text-text-faint uppercase tracking-wider">
                        {agent.status.replace(/_/g, ' ')}
                    </span>
                </div>

                {isRaised && (
                    <div className="animate-bounce bg-status-warning text-white p-1 rounded-md">
                        <Hand className="w-4 h-4" />
                    </div>
                )}
                {isThinking && (
                    <div className="w-2 h-2 rounded-full bg-text-faint animate-pulse" />
                )}
            </div>

            {agent.message && (
                <div className={[
                    'mt-2 text-sm p-2.5 rounded-lg border',
                    isRaised
                        ? 'bg-status-warning/5 border-status-warning/20 text-text-secondary'
                        : 'bg-surface-elevated border-border text-text-muted',
                ].join(' ')}>
                    <div className="flex gap-2">
                        <MessageSquare className="w-3.5 h-3.5 mt-0.5 shrink-0 opacity-50" />
                        <p className="text-sm">{agent.message}</p>
                    </div>
                </div>
            )}
        </div>
    );
};
