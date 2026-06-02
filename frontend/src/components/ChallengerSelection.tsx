import React, { useState } from 'react';
import { DGCard, DGButton } from './ui';
import { ArrowRight, Check, AlertTriangle } from 'lucide-react';

export interface Challenger {
    id: string;
    name: string;
    role: string;
    description: string;
    tags: string[];
    evidenceCount: number;
}

interface ChallengerSelectionProps {
    challengers: Challenger[];
    onStartSimulation: (selectedIds: string[]) => void;
    loadError?: boolean;
}

const AVATAR_COLORS = [
    'bg-[#0176D3]/20 text-[#3392DF]',
    'bg-[#2E844A]/20 text-[#4CAF50]',
    'bg-[#0176D3]/30 text-[#66ADE7]',
    'bg-[#FE9339]/20 text-[#FE9339]',
    'bg-[#0264B0]/20 text-[#3392DF]',
    'bg-[#2E844A]/30 text-[#66BB6A]',
];

export const ChallengerSelection: React.FC<ChallengerSelectionProps> = ({
    challengers,
    onStartSimulation,
    loadError = false,
}) => {
    const [selectedIds, setSelectedIds] = useState<string[]>(
        challengers.slice(0, 3).map(c => c.id)
    );

    const toggleChallenger = (id: string) => {
        setSelectedIds(prev =>
            prev.includes(id)
                ? prev.filter(cId => cId !== id)
                : [...prev, id]
        );
    };

    const isCountOptimal = selectedIds.length >= 2 && selectedIds.length <= 4;

    return (
        <div className="max-w-3xl mx-auto px-4 sm:px-6 min-h-[600px] flex flex-col">
            {/* Header */}
            <div className="mb-8">
                <h1 className="text-3xl font-bold text-white tracking-tight">Choose Your Challengers</h1>
                <div className="w-12 h-1 bg-gradient-to-r from-[#0176D3] to-[#3392DF] rounded-full mt-3 mb-3" />
                <p className="text-white/60 text-sm">
                    Select 2–4 challengers to stress-test your demo.
                </p>
            </div>

            {(loadError || challengers.length === 0) && (
                <div className="rounded-xl border border-[#BA0517]/30 bg-[#BA0517]/10 p-4 mb-4">
                    <div className="flex items-center gap-3 text-[#EF5350]">
                        <AlertTriangle className="w-4 h-4 flex-shrink-0" />
                        <p className="text-sm">
                            {loadError
                                ? "Failed to load challengers — the backend may be unavailable."
                                : "No challengers available."}
                        </p>
                    </div>
                </div>
            )}

            {/* Challenger grid */}
            <div className="flex-1 grid grid-cols-1 sm:grid-cols-2 gap-3">
                {challengers.map((challenger, index) => {
                    const isSelected = selectedIds.includes(challenger.id);
                    const avatarColor = AVATAR_COLORS[index % AVATAR_COLORS.length];

                    return (
                        <DGCard
                            key={challenger.id}
                            className={[
                                'p-5 cursor-pointer transition-all duration-200',
                                isSelected
                                    ? 'border-[#0176D3] bg-[#0176D3]/10 shadow-ai-glow'
                                    : 'hover:border-[#0176D3]/50 hover:shadow-glass-hover',
                            ].join(' ')}
                            onClick={() => toggleChallenger(challenger.id)}
                        >
                            <div className="flex items-start gap-3">
                                <div className={[
                                    'w-10 h-10 rounded-xl flex items-center justify-center text-sm font-bold flex-shrink-0',
                                    avatarColor,
                                ].join(' ')}>
                                    {challenger.name.charAt(0)}
                                </div>

                                <div className="flex-1 min-w-0">
                                    <div className="flex items-center gap-2 mb-0.5">
                                        <h3 className="font-semibold text-sm text-white truncate">
                                            {challenger.name}
                                        </h3>
                                    </div>
                                    <p className="text-xs text-[#0176D3] font-medium uppercase tracking-wide mb-2">{challenger.role}</p>

                                    {challenger.description && (
                                        <p className="text-xs text-white/60 leading-relaxed line-clamp-2 mb-3">
                                            {challenger.description}
                                        </p>
                                    )}

                                    <div className="flex flex-wrap gap-1.5">
                                        {challenger.tags.slice(0, 3).map(tag => (
                                            <span
                                                key={tag}
                                                className="text-[10px] px-2 py-0.5 bg-[#0176D3]/10 text-[#3392DF] border border-[#0176D3]/20 rounded-full font-medium"
                                            >
                                                {tag}
                                            </span>
                                        ))}
                                    </div>
                                </div>

                                <div className="flex-shrink-0">
                                    {isSelected ? (
                                        <div className="w-6 h-6 rounded-lg bg-[#0176D3] flex items-center justify-center shadow-sm">
                                            <Check className="w-3.5 h-3.5 text-white" />
                                        </div>
                                    ) : (
                                        <div className="w-6 h-6 rounded-lg border-2 border-white/20" />
                                    )}
                                </div>
                            </div>
                        </DGCard>
                    );
                })}
            </div>

            {/* Bottom bar */}
            <div className="mt-8 pt-5 border-t border-white/12 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <div className="text-sm text-white/60">
                    <span className="text-white font-semibold">{selectedIds.length}</span> selected
                    {!isCountOptimal && selectedIds.length > 0 && (
                        <span className="text-[#FE9339] ml-2 text-xs">
                            (2–4 recommended)
                        </span>
                    )}
                </div>
                <DGButton
                    variant="primary"
                    size="lg"
                    disabled={selectedIds.length === 0}
                    onClick={() => onStartSimulation(selectedIds)}
                    className="sm:w-auto w-full"
                >
                    Start Demo
                    <ArrowRight className="w-4 h-4 ml-1" />
                </DGButton>
            </div>
        </div>
    );
};
