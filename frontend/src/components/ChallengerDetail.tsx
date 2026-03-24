import React from 'react';
import { BookOpen, Database, FileText, X } from 'lucide-react';
import { Challenge, Fact } from '../api/client';
import { DGIconButton } from './ui';

interface ChallengerDetailProps {
    challenge: Challenge;
    onClose: () => void;
    facts?: Fact[];
    chunks?: string[];
}

export const ChallengerDetail: React.FC<ChallengerDetailProps> = ({ challenge, onClose, facts = [], chunks = [] }) => {
    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 animate-fade-in">
            <div className="absolute inset-0 bg-black/40 backdrop-blur-sm" onClick={onClose} />

            <div className="relative z-10 w-[95vw] sm:max-w-2xl bg-white/95 backdrop-blur-md border border-border-ai rounded-2xl shadow-glass-hover flex flex-col max-h-[90vh]">
                {/* Header */}
                <div className="p-4 sm:p-5 border-b border-border flex items-center justify-between">
                    <div className="flex items-center gap-3">
                        <div className="p-2 bg-ai-50 rounded-xl">
                            <BookOpen className="w-4 h-4 text-ai-500" />
                        </div>
                        <div>
                            <h3 className="text-sm font-semibold text-text-primary">Evidence Inspector</h3>
                            <p className="text-xs text-text-faint">Why the challenger asked this</p>
                        </div>
                    </div>
                    <DGIconButton
                        icon={<X className="w-4 h-4" />}
                        ariaLabel="Close modal"
                        onClick={onClose}
                        size="sm"
                    />
                </div>

                {/* Content */}
                <div className="p-4 sm:p-5 overflow-y-auto space-y-5 flex-1">
                    {/* The Question */}
                    <div className="bg-ai-50/50 border border-ai-200/50 rounded-xl p-4">
                        <p className="text-[10px] font-medium text-ai-500 uppercase tracking-wider mb-2">The Challenge</p>
                        <p className="text-base text-text-primary font-medium leading-relaxed">
                            &ldquo;{challenge.question}&rdquo;
                        </p>
                    </div>

                    {/* Deck Evidence */}
                    <div>
                        <div className="flex items-center gap-2 mb-3">
                            <FileText className="w-4 h-4 text-ai-500" />
                            <h4 className="text-sm font-semibold text-text-primary">Deck Context</h4>
                        </div>
                        {chunks.length > 0 ? (
                            <div className="space-y-2">
                                {chunks.map((chunk, i) => (
                                    <div key={i} className="bg-ai-50/40 border border-ai-100 rounded-xl p-3 text-text-secondary text-sm leading-relaxed">
                                        &ldquo;{chunk}&rdquo;
                                    </div>
                                ))}
                            </div>
                        ) : (
                            <p className="text-text-faint text-sm">No specific deck chunks cited.</p>
                        )}
                    </div>

                    {/* Research Facts */}
                    <div>
                        <div className="flex items-center gap-2 mb-3">
                            <Database className="w-4 h-4 text-status-success" />
                            <h4 className="text-sm font-semibold text-text-primary">Research Facts</h4>
                        </div>
                        {facts.length > 0 ? (
                            <div className="space-y-2">
                                {facts.map((fact, i) => (
                                    <div key={i} className="bg-status-success/5 border border-status-success/15 rounded-xl p-3">
                                        <p className="text-text-secondary text-sm mb-1.5">&ldquo;{fact.text}&rdquo;</p>
                                        <div className="flex items-center justify-between text-xs text-text-faint">
                                            <span className="text-status-success font-mono">{fact.topic}</span>
                                            <span className="truncate max-w-[180px]">{fact.source_title}</span>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        ) : (
                            <p className="text-text-faint text-sm">No specific research facts cited.</p>
                        )}
                    </div>

                    {/* Ideal Answer */}
                    <div className="border-t border-border pt-4">
                        <p className="text-[10px] font-medium text-text-faint uppercase tracking-wider mb-2">Ideal Answer Strategy</p>
                        <p className="text-text-secondary leading-relaxed bg-white/60 p-3 rounded-xl border border-border text-sm">
                            {challenge.ideal_answer}
                        </p>
                    </div>
                </div>
            </div>
        </div>
    );
};
