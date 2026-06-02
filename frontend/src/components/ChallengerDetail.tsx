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
            <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" onClick={onClose} />

            <div className="relative z-10 w-[95vw] sm:max-w-2xl bg-[#0A3D6B]/95 backdrop-blur-md border border-[#0176D3]/25 rounded-2xl shadow-glass-hover flex flex-col max-h-[90vh]">
                {/* Header */}
                <div className="p-4 sm:p-5 border-b border-white/12 flex items-center justify-between">
                    <div className="flex items-center gap-3">
                        <div className="p-2 bg-[#0176D3]/15 rounded-xl">
                            <BookOpen className="w-4 h-4 text-[#0176D3]" />
                        </div>
                        <div>
                            <h3 className="text-sm font-semibold text-white">Evidence Inspector</h3>
                            <p className="text-xs text-white/40">Why the challenger asked this</p>
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
                    <div className="bg-[#032D60]/60 border border-[#0176D3]/20 rounded-xl p-4">
                        <p className="text-[10px] font-medium text-[#0176D3] uppercase tracking-wider mb-2">The Challenge</p>
                        <p className="text-base text-white font-medium leading-relaxed">
                            &ldquo;{challenge.question}&rdquo;
                        </p>
                    </div>

                    {/* Deck Evidence */}
                    <div>
                        <div className="flex items-center gap-2 mb-3">
                            <FileText className="w-4 h-4 text-[#0176D3]" />
                            <h4 className="text-sm font-semibold text-white">Deck Context</h4>
                        </div>
                        {chunks.length > 0 ? (
                            <div className="space-y-2">
                                {chunks.map((chunk, i) => (
                                    <div key={i} className="bg-[#032D60]/40 border border-[#0176D3]/15 rounded-xl p-3 text-white/85 text-sm leading-relaxed">
                                        &ldquo;{chunk}&rdquo;
                                    </div>
                                ))}
                            </div>
                        ) : (
                            <p className="text-white/40 text-sm">No specific deck chunks cited.</p>
                        )}
                    </div>

                    {/* Research Facts */}
                    <div>
                        <div className="flex items-center gap-2 mb-3">
                            <Database className="w-4 h-4 text-[#2E844A]" />
                            <h4 className="text-sm font-semibold text-white">Research Facts</h4>
                        </div>
                        {facts.length > 0 ? (
                            <div className="space-y-2">
                                {facts.map((fact, i) => (
                                    <div key={i} className="bg-[#2E844A]/10 border border-[#2E844A]/20 rounded-xl p-3">
                                        <p className="text-white/85 text-sm mb-1.5">&ldquo;{fact.text}&rdquo;</p>
                                        <div className="flex items-center justify-between text-xs text-white/40">
                                            <span className="text-[#4CAF50] font-mono">{fact.topic}</span>
                                            <span className="truncate max-w-[180px]">{fact.source_title}</span>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        ) : (
                            <p className="text-white/40 text-sm">No specific research facts cited.</p>
                        )}
                    </div>

                    {/* Ideal Answer */}
                    <div className="border-t border-white/12 pt-4">
                        <p className="text-[10px] font-medium text-white/40 uppercase tracking-wider mb-2">Ideal Answer Strategy</p>
                        <p className="text-white/85 leading-relaxed bg-[#032D60]/40 p-3 rounded-xl border border-white/8 text-sm">
                            {challenge.ideal_answer}
                        </p>
                    </div>
                </div>
            </div>
        </div>
    );
};
