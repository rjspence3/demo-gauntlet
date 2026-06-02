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
            <header className="flex justify-between items-center pb-4 border-b border-white/12">
                <div>
                    <div className="flex items-center gap-3 mb-1">
                        <h1 className="text-xl font-bold text-white tracking-tight">
                            Live Gauntlet
                        </h1>
                        <DGBadge variant="warning">Beta</DGBadge>
                    </div>
                    <p className="text-white/60 text-sm">Present your deck. Agents will raise their hand with questions.</p>
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
                                <p className="text-[10px] text-white/40 font-mono text-center mb-2 uppercase tracking-wider">Live Transcript</p>
                                {transcriptHistory.map((t, i) => (
                                    <p key={i} className="text-white/85 text-sm text-center animate-fade-in">
                                        &ldquo;{t}&rdquo;
                                    </p>
                                ))}
                                {transcriptHistory.length === 0 && (
                                    <p className="text-white/40 text-sm text-center">
                                        Words will appear here...
                                    </p>
                                )}
                            </div>
                        </div>
                    </DGCard>
                </div>

                {/* Agent Gallery */}
                <DGCard className="flex flex-col gap-3 p-4">
                    <h2 className="text-sm font-semibold text-white flex items-center gap-2">
                        <User className="w-4 h-4 text-[#0176D3]" />
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
                'p-3 rounded-xl border transition-all duration-300',
                isRaised
                    ? 'border-[#FE9339]/30 bg-[#FE9339]/10'
                    : 'border-[#0176D3]/25 bg-[#032D60]/50 backdrop-blur-sm',
            ].join(' ')}
        >
            <div className="flex items-start justify-between">
                <div>
                    <h3 className="font-semibold text-sm text-white">
                        {displayName}
                    </h3>
                    <span className="text-[10px] text-white/40 uppercase tracking-wider">
                        {agent.status.replace(/_/g, ' ')}
                    </span>
                </div>

                {isRaised && (
                    <div className="animate-bounce bg-[#FE9339] text-white p-1 rounded-lg">
                        <Hand className="w-4 h-4" />
                    </div>
                )}
                {isThinking && (
                    <div className="w-2 h-2 rounded-full bg-[#0176D3] animate-soft-pulse" />
                )}
            </div>

            {agent.message && (
                <div className={[
                    'mt-2 text-sm p-2.5 rounded-xl border',
                    isRaised
                        ? 'bg-[#FE9339]/5 border-[#FE9339]/20 text-white/85'
                        : 'bg-[#032D60]/40 border-white/8 text-white/60',
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
