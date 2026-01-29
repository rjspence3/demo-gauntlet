import React from 'react';
import { BookOpen, Database, FileText, X } from 'lucide-react';
import { Challenge, Fact } from '../api/client';
import { DGModal, DGCard, DGIconButton } from './ui';

/**
 * Props for the ChallengerDetail component.
 */
interface ChallengerDetailProps {
    /** The challenge to display details for. */
    challenge: Challenge;
    /** Callback to close the detail view. */
    onClose: () => void;
    /** Optional list of research facts used as evidence. */
    facts?: Fact[];
    /** Optional list of deck chunks used as evidence. */
    chunks?: string[];
}

/**
 * Component for displaying detailed evidence and reasoning behind a challenge.
 */
export const ChallengerDetail: React.FC<ChallengerDetailProps> = ({ challenge, onClose, facts = [], chunks = [] }) => {
    return (
        <DGModal isOpen={true} onClose={onClose} size="lg">
            {/* Header */}
            <div className="p-4 sm:p-6 border-b border-slate-800 flex items-center justify-between">
                <div className="flex items-center space-x-3">
                    <div className="p-2 bg-cyan-400/10 rounded-lg">
                        <BookOpen className="w-5 sm:w-6 h-5 sm:h-6 text-cyan-400" />
                    </div>
                    <div>
                        <h3 className="text-lg sm:text-xl font-bold text-white">Evidence Inspector</h3>
                        <p className="text-xs sm:text-sm text-slate-400">Why the challenger asked this question</p>
                    </div>
                </div>
                <DGIconButton
                    icon={<X className="w-5 h-5" />}
                    ariaLabel="Close modal"
                    onClick={onClose}
                />
            </div>

            {/* Content */}
            <div className="p-4 sm:p-6 overflow-y-auto space-y-6 sm:space-y-8 max-h-[60vh]">

                {/* The Question */}
                <DGCard variant="bordered" className="p-4 sm:p-6">
                    <h4 className="text-xs sm:text-sm font-bold text-slate-500 uppercase tracking-wider mb-2">The Challenge</h4>
                    <p className="text-lg sm:text-xl text-white font-medium leading-relaxed">
                        "{challenge.question}"
                    </p>
                </DGCard>

                {/* Deck Evidence */}
                <div>
                    <div className="flex items-center space-x-2 mb-3 sm:mb-4">
                        <FileText className="w-4 sm:w-5 h-4 sm:h-5 text-violet-400" />
                        <h4 className="text-base sm:text-lg font-bold text-white">Deck Context</h4>
                    </div>
                    {chunks.length > 0 ? (
                        <div className="space-y-3">
                            {chunks.map((chunk, i) => (
                                <div key={i} className="bg-violet-500/5 border border-violet-500/20 rounded-xl p-3 sm:p-4 text-slate-300 text-sm leading-relaxed">
                                    "{chunk}"
                                </div>
                            ))}
                        </div>
                    ) : (
                        <p className="text-slate-500 italic text-sm">No specific deck chunks cited.</p>
                    )}
                </div>

                {/* Research Facts */}
                <div>
                    <div className="flex items-center space-x-2 mb-3 sm:mb-4">
                        <Database className="w-4 sm:w-5 h-4 sm:h-5 text-emerald-400" />
                        <h4 className="text-base sm:text-lg font-bold text-white">Research Facts</h4>
                    </div>
                    {facts.length > 0 ? (
                        <div className="space-y-3">
                            {facts.map((fact, i) => (
                                <div key={i} className="bg-emerald-500/5 border border-emerald-500/20 rounded-xl p-3 sm:p-4">
                                    <p className="text-slate-300 text-sm mb-2">"{fact.text}"</p>
                                    <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-1 text-xs text-slate-500">
                                        <span className="font-mono text-emerald-400">{fact.topic}</span>
                                        <span className="truncate max-w-full sm:max-w-[200px]">{fact.source_title}</span>
                                    </div>
                                </div>
                            ))}
                        </div>
                    ) : (
                        <p className="text-slate-500 italic text-sm">No specific research facts cited.</p>
                    )}
                </div>

                {/* Ideal Answer */}
                <div className="border-t border-slate-800 pt-4 sm:pt-6">
                    <h4 className="text-xs sm:text-sm font-bold text-slate-500 uppercase tracking-wider mb-2">Ideal Answer Strategy</h4>
                    <p className="text-slate-300 leading-relaxed bg-slate-800/50 p-3 sm:p-4 rounded-xl border border-slate-700 text-sm">
                        {challenge.ideal_answer}
                    </p>
                </div>

            </div>
        </DGModal>
    );
};
