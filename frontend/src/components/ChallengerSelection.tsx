import React, { useState } from 'react';
import { DGCard, DGButton } from './ui';
import { ArrowRight, CheckCircle2, AlertTriangle } from 'lucide-react';

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

// Deterministic color palette for persona avatars
const AVATAR_COLORS = [
    'bg-violet-100 text-violet-700',
    'bg-blue-100 text-blue-700',
    'bg-emerald-100 text-emerald-700',
    'bg-rose-100 text-rose-700',
    'bg-amber-100 text-amber-700',
    'bg-cyan-100 text-cyan-700',
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
        <div className="max-w-5xl mx-auto p-4 sm:p-6 min-h-[600px] flex flex-col">
            <div className="mb-8">
                <h1 className="text-3xl font-bold text-slate-900">Choose Your Challengers</h1>
                <p className="text-slate-600 mt-2">
                    Select who will be in the room. We recommend 2–4 challengers based on your deck's content.
                </p>
            </div>

            {(loadError || challengers.length === 0) && (
                <DGCard className="p-6 mb-4 border-rose-200 bg-rose-50">
                    <div className="flex items-center gap-3 text-rose-600">
                        <AlertTriangle className="w-5 h-5 flex-shrink-0" />
                        <div>
                            <p className="font-medium text-sm">
                                {loadError
                                    ? "Failed to load challengers — the backend may be unavailable."
                                    : "No challengers available. The backend returned an empty list."}
                            </p>
                            <p className="text-xs text-rose-500 mt-0.5">Try refreshing the page. If the issue persists, contact support.</p>
                        </div>
                    </div>
                </DGCard>
            )}

            <div className="flex-1 space-y-3">
                {challengers.map((challenger, index) => {
                    const isSelected = selectedIds.includes(challenger.id);
                    const avatarColor = AVATAR_COLORS[index % AVATAR_COLORS.length];

                    return (
                        <DGCard
                            key={challenger.id}
                            className={[
                                'p-4 sm:p-5 cursor-pointer transition-all duration-200',
                                isSelected
                                    ? 'border-orange-300 bg-orange-50/50 shadow-sm'
                                    : 'border-slate-200 hover:border-slate-300 hover:shadow-sm',
                            ].join(' ')}
                            onClick={() => toggleChallenger(challenger.id)}
                        >
                            <div className="flex items-center gap-4">
                                {/* Colored avatar */}
                                <div className={[
                                    'w-10 h-10 rounded-full flex items-center justify-center text-sm font-bold flex-shrink-0',
                                    avatarColor,
                                ].join(' ')}>
                                    {challenger.name.charAt(0)}
                                </div>

                                {/* Identity */}
                                <div className="flex-1 min-w-0">
                                    <div className="flex flex-wrap items-center gap-2 mb-1">
                                        <h3 className={`font-semibold text-sm ${isSelected ? 'text-slate-900' : 'text-slate-700'}`}>
                                            {challenger.name}
                                        </h3>
                                        <span className="text-xs text-slate-500">{challenger.role}</span>
                                    </div>

                                    {challenger.description && (
                                        <p className="text-xs text-slate-500 mb-1 leading-relaxed line-clamp-2">
                                            {challenger.description}
                                        </p>
                                    )}

                                    {/* Tags */}
                                    <div className="hidden sm:flex flex-wrap gap-1">
                                        {challenger.tags.slice(0, 3).map(tag => (
                                            <span
                                                key={tag}
                                                className="text-[10px] px-1.5 py-0.5 bg-slate-100 text-slate-500 rounded font-mono"
                                            >
                                                #{tag}
                                            </span>
                                        ))}
                                    </div>
                                </div>

                                {/* Selection indicator */}
                                <div className="flex-shrink-0 ml-2">
                                    {isSelected ? (
                                        <CheckCircle2 className="w-5 h-5 text-orange-500" />
                                    ) : (
                                        <div className="w-5 h-5 rounded-full border-2 border-slate-300" />
                                    )}
                                </div>
                            </div>
                        </DGCard>
                    );
                })}
            </div>

            <div className="mt-8 pt-6 border-t border-slate-200 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <div className="text-sm text-slate-500">
                    <span className="text-slate-900 font-medium">{selectedIds.length}</span> challenger{selectedIds.length !== 1 ? 's' : ''} selected
                    {!isCountOptimal && selectedIds.length > 0 && (
                        <span className="text-amber-600 ml-2">
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
                    Enter Demo Room
                    <ArrowRight className="w-4 h-4 ml-2" />
                </DGButton>
            </div>
        </div>
    );
};
