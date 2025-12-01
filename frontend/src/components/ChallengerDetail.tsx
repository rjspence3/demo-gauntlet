import React from 'react';
import { BookOpen, Database, FileText, X } from 'lucide-react';
import { Challenge, Slide, Fact } from '../api/client'; // Assuming Fact is added to client types
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

interface ChallengerDetailProps {
    challenge: Challenge;
    onClose: () => void;
    facts?: Fact[]; // Optional for now
    chunks?: string[]; // Optional for now
}

export const ChallengerDetail: React.FC<ChallengerDetailProps> = ({ challenge, onClose, facts = [], chunks = [] }) => {
    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-fade-in">
            <div className="bg-gray-900 border border-neon-blue/30 rounded-2xl w-full max-w-2xl max-h-[80vh] overflow-hidden flex flex-col shadow-[0_0_50px_rgba(0,243,255,0.1)]">
                {/* Header */}
                <div className="p-6 border-b border-white/10 flex items-center justify-between bg-white/5">
                    <div className="flex items-center space-x-3">
                        <div className="p-2 bg-neon-blue/10 rounded-lg">
                            <BookOpen className="w-6 h-6 text-neon-blue" />
                        </div>
                        <div>
                            <h3 className="text-xl font-bold text-white font-display">Evidence Inspector</h3>
                            <p className="text-sm text-gray-400">Why the challenger asked this question</p>
                        </div>
                    </div>
                    <button
                        onClick={onClose}
                        className="p-2 hover:bg-white/10 rounded-full transition-colors text-gray-400 hover:text-white"
                    >
                        <X className="w-6 h-6" />
                    </button>
                </div>

                {/* Content */}
                <div className="p-6 overflow-y-auto space-y-8 custom-scrollbar">

                    {/* The Question */}
                    <div className="bg-white/5 rounded-xl p-6 border border-white/5">
                        <h4 className="text-sm font-bold text-gray-500 uppercase tracking-wider mb-2">The Challenge</h4>
                        <p className="text-xl text-white font-medium leading-relaxed">
                            "{challenge.question}"
                        </p>
                    </div>

                    {/* Deck Evidence */}
                    <div>
                        <div className="flex items-center space-x-2 mb-4">
                            <FileText className="w-5 h-5 text-neon-purple" />
                            <h4 className="text-lg font-bold text-white">Deck Context</h4>
                        </div>
                        {chunks.length > 0 ? (
                            <div className="space-y-3">
                                {chunks.map((chunk, i) => (
                                    <div key={i} className="bg-neon-purple/5 border border-neon-purple/20 rounded-lg p-4 text-gray-300 text-sm leading-relaxed">
                                        "{chunk}"
                                    </div>
                                ))}
                            </div>
                        ) : (
                            <p className="text-gray-500 italic">No specific deck chunks cited.</p>
                        )}
                    </div>

                    {/* Research Facts */}
                    <div>
                        <div className="flex items-center space-x-2 mb-4">
                            <Database className="w-5 h-5 text-neon-green" />
                            <h4 className="text-lg font-bold text-white">Research Facts</h4>
                        </div>
                        {facts.length > 0 ? (
                            <div className="space-y-3">
                                {facts.map((fact, i) => (
                                    <div key={i} className="bg-neon-green/5 border border-neon-green/20 rounded-lg p-4">
                                        <p className="text-gray-300 text-sm mb-2">"{fact.text}"</p>
                                        <div className="flex items-center justify-between text-xs text-gray-500">
                                            <span className="font-mono text-neon-green">{fact.topic}</span>
                                            <span className="truncate max-w-[200px]">{fact.source_title}</span>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        ) : (
                            <p className="text-gray-500 italic">No specific research facts cited.</p>
                        )}
                    </div>

                    {/* Ideal Answer (Hidden/Revealed logic could be added, showing for now) */}
                    <div className="border-t border-white/10 pt-6">
                        <h4 className="text-sm font-bold text-gray-500 uppercase tracking-wider mb-2">Ideal Answer Strategy</h4>
                        <p className="text-gray-300 leading-relaxed bg-gray-800/50 p-4 rounded-lg border border-white/5">
                            {challenge.ideal_answer}
                        </p>
                    </div>

                </div>
            </div>
        </div>
    );
};
