import React, { useState, useMemo } from 'react';
import { Database, FileText, X, User, MessageSquare, HelpCircle, ExternalLink } from 'lucide-react';
import { ChallengerPersona, Challenge, Fact } from '../api/client';
import { cn } from '../lib/utils';
import { DGModal, DGCard, DGIconButton, DGTag } from './ui';

/**
 * Props for the ChallengerPersonaDetail component.
 */
interface ChallengerPersonaDetailProps {
    /** The persona to display details for. */
    persona: ChallengerPersona;
    /** List of challenges associated with this persona. */
    challenges: Challenge[];
    /** Callback to close the detail view. */
    onClose: () => void;
}

type Tab = 'overview' | 'evidence' | 'research' | 'qa';

/**
 * Component for displaying detailed information about a challenger persona.
 */
export const ChallengerPersonaDetail: React.FC<ChallengerPersonaDetailProps> = ({ persona, challenges, onClose }) => {
    const [activeTab, setActiveTab] = useState<Tab>('overview');

    // Aggregate evidence
    const { allChunks, allFacts } = useMemo(() => {
        const chunks = new Set<string>();
        const factsMap = new Map<string, Fact>();

        challenges.forEach(c => {
            if (c.evidence?.chunks) {
                c.evidence.chunks.forEach(chunk => chunks.add(chunk));
            }
            if (c.evidence?.facts) {
                c.evidence.facts.forEach(fact => {
                    const key = fact.id || fact.text;
                    if (!factsMap.has(key)) {
                        factsMap.set(key, fact);
                    }
                });
            }
        });

        return {
            allChunks: Array.from(chunks),
            allFacts: Array.from(factsMap.values())
        };
    }, [challenges]);

    const tabs = [
        { id: 'overview' as Tab, label: 'Overview', shortLabel: 'Info', icon: User },
        { id: 'evidence' as Tab, label: 'Deck Evidence', shortLabel: 'Deck', icon: FileText },
        { id: 'research' as Tab, label: 'Research Facts', shortLabel: 'Research', icon: Database },
        { id: 'qa' as Tab, label: 'Q&A Preview', shortLabel: 'Q&A', icon: MessageSquare },
    ];

    return (
        <DGModal isOpen={true} onClose={onClose} size="xl">
            {/* Header */}
            <div className="p-4 sm:p-6 border-b border-slate-800 flex items-center justify-between">
                <div className="flex items-center space-x-3 sm:space-x-4">
                    <div className="w-10 h-10 sm:w-12 sm:h-12 bg-cyan-400/10 rounded-xl flex items-center justify-center border border-cyan-400/20">
                        <User className="w-5 h-5 sm:w-6 sm:h-6 text-cyan-400" />
                    </div>
                    <div>
                        <h3 className="text-xl sm:text-2xl font-bold text-white">{persona.name}</h3>
                        <div className="flex items-center space-x-2 text-xs sm:text-sm text-slate-400">
                            <span>{persona.role}</span>
                            <span className="w-1 h-1 rounded-full bg-slate-600"></span>
                            <span>{challenges.length} Challenges</span>
                        </div>
                    </div>
                </div>
                <DGIconButton
                    icon={<X className="w-5 h-5" />}
                    ariaLabel="Close modal"
                    onClick={onClose}
                />
            </div>

            {/* Tabs */}
            <div className="flex border-b border-slate-800 px-2 sm:px-6 bg-slate-900/50 overflow-x-auto">
                {tabs.map(tab => (
                    <button
                        key={tab.id}
                        onClick={() => setActiveTab(tab.id)}
                        className={cn(
                            "flex items-center space-x-1.5 sm:space-x-2 px-3 sm:px-6 py-3 sm:py-4 text-xs sm:text-sm font-bold border-b-2 transition-all whitespace-nowrap",
                            activeTab === tab.id
                                ? "border-cyan-400 text-white bg-slate-800/50"
                                : "border-transparent text-slate-500 hover:text-slate-300 hover:bg-slate-800/30"
                        )}
                    >
                        <tab.icon className="w-4 h-4" />
                        <span className="hidden sm:inline">{tab.label}</span>
                        <span className="sm:hidden">{tab.shortLabel}</span>
                    </button>
                ))}
            </div>

            {/* Content */}
            <div className="flex-grow overflow-y-auto p-4 sm:p-8 bg-slate-950/50 max-h-[60vh]">

                {activeTab === 'overview' && (
                    <div className="space-y-6 sm:space-y-8 animate-fade-in">
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 sm:gap-6">
                            <DGCard variant="bordered" className="p-4 sm:p-6">
                                <h4 className="text-xs sm:text-sm font-bold text-slate-500 uppercase tracking-wider mb-3 sm:mb-4">Persona Style</h4>
                                <p className="text-base sm:text-lg text-slate-200 leading-relaxed">
                                    "{persona.style}"
                                </p>
                            </DGCard>
                            <DGCard variant="bordered" className="p-4 sm:p-6">
                                <h4 className="text-xs sm:text-sm font-bold text-slate-500 uppercase tracking-wider mb-3 sm:mb-4">Focus Areas</h4>
                                <div className="flex flex-wrap gap-2">
                                    {persona.focus_areas.map(area => (
                                        <DGTag key={area} variant="accent">{area}</DGTag>
                                    ))}
                                </div>
                            </DGCard>
                        </div>

                        <div>
                            <h4 className="text-xs sm:text-sm font-bold text-slate-500 uppercase tracking-wider mb-3 sm:mb-4">Reasoning Capabilities</h4>
                            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 sm:gap-4">
                                <DGCard className="p-3 sm:p-4 flex items-center space-x-3">
                                    <FileText className="w-4 sm:w-5 h-4 sm:h-5 text-violet-400" />
                                    <span className="text-slate-300 text-sm">Deck Analysis</span>
                                </DGCard>
                                <DGCard className="p-3 sm:p-4 flex items-center space-x-3">
                                    <Database className="w-4 sm:w-5 h-4 sm:h-5 text-emerald-400" />
                                    <span className="text-slate-300 text-sm">Fact Checking</span>
                                </DGCard>
                                <DGCard className="p-3 sm:p-4 flex items-center space-x-3">
                                    <HelpCircle className="w-4 sm:w-5 h-4 sm:h-5 text-pink-400" />
                                    <span className="text-slate-300 text-sm">Strategic Questioning</span>
                                </DGCard>
                            </div>
                        </div>
                    </div>
                )}

                {activeTab === 'evidence' && (
                    <div className="space-y-4 sm:space-y-6 animate-fade-in">
                        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 mb-2">
                            <h4 className="text-base sm:text-lg font-bold text-white">Referenced Deck Content</h4>
                            <span className="text-xs sm:text-sm text-slate-500">{allChunks.length} excerpts found</span>
                        </div>

                        {allChunks.length > 0 ? (
                            <div className="grid gap-3 sm:gap-4">
                                {allChunks.map((chunk, i) => (
                                    <div key={i} className="bg-violet-500/5 border border-violet-500/20 rounded-xl p-4 sm:p-5 hover:bg-violet-500/10 transition-colors">
                                        <div className="flex items-start space-x-3">
                                            <FileText className="w-4 sm:w-5 h-4 sm:h-5 text-violet-400 mt-0.5 flex-shrink-0" />
                                            <p className="text-slate-300 text-sm leading-relaxed">"{chunk}"</p>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        ) : (
                            <DGCard variant="bordered" className="text-center py-10 sm:py-12 border-dashed">
                                <span className="text-slate-500 italic text-sm">No specific deck chunks referenced yet.</span>
                            </DGCard>
                        )}
                    </div>
                )}

                {activeTab === 'research' && (
                    <div className="space-y-4 sm:space-y-6 animate-fade-in">
                        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 mb-2">
                            <h4 className="text-base sm:text-lg font-bold text-white">External Research Facts</h4>
                            <span className="text-xs sm:text-sm text-slate-500">{allFacts.length} facts verified</span>
                        </div>

                        {allFacts.length > 0 ? (
                            <div className="grid gap-3 sm:gap-4">
                                {allFacts.map((fact, i) => (
                                    <div key={i} className="bg-emerald-500/5 border border-emerald-500/20 rounded-xl p-4 sm:p-5 hover:bg-emerald-500/10 transition-colors">
                                        <div className="flex items-start space-x-3 mb-3">
                                            <Database className="w-4 sm:w-5 h-4 sm:h-5 text-emerald-400 mt-0.5 flex-shrink-0" />
                                            <div>
                                                <p className="text-slate-200 text-sm font-medium mb-1">"{fact.text}"</p>
                                                <p className="text-xs text-slate-400">{fact.snippet}</p>
                                            </div>
                                        </div>
                                        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 pt-3 border-t border-emerald-500/10">
                                            <span className="text-xs font-mono text-emerald-400 px-2 py-1 rounded bg-emerald-500/10 w-fit">
                                                {fact.topic}
                                            </span>
                                            <a
                                                href={fact.source_url}
                                                target="_blank"
                                                rel="noopener noreferrer"
                                                className="text-xs text-slate-500 hover:text-white truncate max-w-full sm:max-w-[300px] flex items-center"
                                            >
                                                {fact.source_title}
                                                <ExternalLink className="w-3 h-3 ml-1 flex-shrink-0" />
                                            </a>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        ) : (
                            <DGCard variant="bordered" className="text-center py-10 sm:py-12 border-dashed">
                                <span className="text-slate-500 italic text-sm">No external research facts referenced yet.</span>
                            </DGCard>
                        )}
                    </div>
                )}

                {activeTab === 'qa' && (
                    <div className="space-y-4 sm:space-y-6 animate-fade-in">
                        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 mb-2">
                            <h4 className="text-base sm:text-lg font-bold text-white">Generated Challenge Set</h4>
                            <span className="text-xs sm:text-sm text-slate-500">{challenges.length} questions prepared</span>
                        </div>

                        {challenges.length > 0 ? (
                            <div className="space-y-3 sm:space-y-4">
                                {challenges.map((challenge, i) => (
                                    <DGCard key={i} className="overflow-hidden">
                                        <div className="p-4 sm:p-5 border-b border-slate-800 bg-slate-900/50">
                                            <div className="flex items-start space-x-3">
                                                <HelpCircle className="w-4 sm:w-5 h-4 sm:h-5 text-pink-400 mt-0.5 flex-shrink-0" />
                                                <p className="text-white font-medium text-sm sm:text-base">{challenge.question}</p>
                                            </div>
                                        </div>
                                        <div className="p-4 sm:p-5 bg-slate-800/30">
                                            <h5 className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">Ideal Answer Strategy</h5>
                                            <p className="text-slate-400 text-sm leading-relaxed">{challenge.ideal_answer}</p>
                                        </div>
                                    </DGCard>
                                ))}
                            </div>
                        ) : (
                            <DGCard variant="bordered" className="text-center py-10 sm:py-12 border-dashed">
                                <span className="text-slate-500 italic text-sm">No challenges generated yet.</span>
                            </DGCard>
                        )}
                    </div>
                )}

            </div>
        </DGModal>
    );
};
