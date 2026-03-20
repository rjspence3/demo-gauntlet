import React, { useState } from 'react';
import { DGCard, DGButton } from './ui';
import { ArrowRight, CheckCircle2 } from 'lucide-react';

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
}

export const ChallengerSelection: React.FC<ChallengerSelectionProps> = ({
    challengers,
    onStartSimulation,
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
                <h1 className="text-3xl font-bold text-white">Choose Your Challengers</h1>
                <p className="text-slate-400 mt-2">
                    Select who will be in the room. We recommend 2–4 challengers based on your deck's content.
                </p>
            </div>

            <div className="flex-1 space-y-3">
                {challengers.map((challenger) => {
                    const isSelected = selectedIds.includes(challenger.id);
                    const evidencePercent = Math.min(100, (challenger.evidenceCount / 10) * 100);

                    return (
                        <DGCard
                            key={challenger.id}
                            className={[
                                'p-4 sm:p-5 cursor-pointer transition-all duration-200',
                                isSelected
                                    ? 'border-cyan-400/40 bg-cyan-400/5'
                                    : 'border-slate-800 opacity-70 hover:opacity-90 hover:border-slate-700',
                            ].join(' ')}
                            onClick={() => toggleChallenger(challenger.id)}
                        >
                            <div className="flex items-center gap-4">
                                {/* Avatar */}
                                <div className={[
                                    'w-10 h-10 rounded-full flex items-center justify-center text-sm font-bold flex-shrink-0',
                                    isSelected ? 'bg-cyan-400/20 text-cyan-400' : 'bg-slate-800 text-slate-500',
                                ].join(' ')}>
                                    {challenger.name.charAt(0)}
                                </div>

                                {/* Identity */}
                                <div className="flex-1 min-w-0">
                                    <div className="flex flex-wrap items-center gap-2 mb-1">
                                        <h3 className={`font-semibold text-sm ${isSelected ? 'text-white' : 'text-slate-400'}`}>
                                            {challenger.name}
                                        </h3>
                                        <span className="text-xs text-slate-500">{challenger.role}</span>
                                    </div>

                                    {/* Evidence bar + tags */}
                                    <div className="flex items-center gap-3">
                                        <div className="flex-1 max-w-[120px] h-1 bg-slate-800 rounded-full overflow-hidden">
                                            <div
                                                className={`h-full rounded-full ${isSelected ? 'bg-cyan-400' : 'bg-slate-600'}`}
                                                style={{ width: `${evidencePercent}%` }}
                                            />
                                        </div>
                                        <span className="text-[11px] text-slate-500 flex-shrink-0">
                                            {challenger.evidenceCount} facts
                                        </span>
                                        <div className="hidden sm:flex flex-wrap gap-1">
                                            {challenger.tags.slice(0, 3).map(tag => (
                                                <span
                                                    key={tag}
                                                    className="text-[10px] px-1.5 py-0.5 bg-slate-800 text-slate-500 rounded font-mono"
                                                >
                                                    #{tag}
                                                </span>
                                            ))}
                                        </div>
                                    </div>
                                </div>

                                {/* Selection indicator */}
                                <div className="flex-shrink-0 ml-2">
                                    {isSelected ? (
                                        <CheckCircle2 className="w-5 h-5 text-cyan-400" />
                                    ) : (
                                        <div className="w-5 h-5 rounded-full border-2 border-slate-700" />
                                    )}
                                </div>
                            </div>
                        </DGCard>
                    );
                })}
            </div>

            <div className="mt-8 pt-6 border-t border-slate-800 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <div className="text-sm text-slate-500">
                    <span className="text-white font-medium">{selectedIds.length}</span> challenger{selectedIds.length !== 1 ? 's' : ''} selected
                    {!isCountOptimal && selectedIds.length > 0 && (
                        <span className="text-amber-400 ml-2">
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
