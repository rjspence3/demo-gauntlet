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
    'bg-accent-purple/15 text-accent-purple',
    'bg-blue-500/15 text-blue-400',
    'bg-status-success/15 text-status-success',
    'bg-brand-500/15 text-brand-400',
    'bg-status-warning/15 text-status-warning',
    'bg-cyan-500/15 text-cyan-400',
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
            <div className="mb-8">
                <h1 className="text-2xl font-semibold text-text-primary">Choose Your Challengers</h1>
                <p className="text-text-muted text-sm mt-2">
                    Select 2–4 challengers to stress-test your demo.
                </p>
            </div>

            {(loadError || challengers.length === 0) && (
                <div className="rounded-lg border border-status-error/20 bg-status-error/5 p-4 mb-4">
                    <div className="flex items-center gap-3 text-status-error">
                        <AlertTriangle className="w-4 h-4 flex-shrink-0" />
                        <p className="text-sm">
                            {loadError
                                ? "Failed to load challengers — the backend may be unavailable."
                                : "No challengers available."}
                        </p>
                    </div>
                </div>
            )}

            <div className="flex-1 grid grid-cols-1 sm:grid-cols-2 gap-3">
                {challengers.map((challenger, index) => {
                    const isSelected = selectedIds.includes(challenger.id);
                    const avatarColor = AVATAR_COLORS[index % AVATAR_COLORS.length];

                    return (
                        <DGCard
                            key={challenger.id}
                            className={[
                                'p-4 cursor-pointer transition-all duration-150',
                                isSelected
                                    ? 'border-brand-500/50 bg-brand-500/5'
                                    : 'border-border hover:border-border-hover',
                            ].join(' ')}
                            onClick={() => toggleChallenger(challenger.id)}
                        >
                            <div className="flex items-start gap-3">
                                <div className={[
                                    'w-9 h-9 rounded-lg flex items-center justify-center text-xs font-bold flex-shrink-0',
                                    avatarColor,
                                ].join(' ')}>
                                    {challenger.name.charAt(0)}
                                </div>

                                <div className="flex-1 min-w-0">
                                    <div className="flex items-center gap-2 mb-0.5">
                                        <h3 className="font-medium text-sm text-text-primary truncate">
                                            {challenger.name}
                                        </h3>
                                    </div>
                                    <p className="text-xs text-text-muted mb-2">{challenger.role}</p>

                                    {challenger.description && (
                                        <p className="text-xs text-text-faint leading-relaxed line-clamp-2 mb-2">
                                            {challenger.description}
                                        </p>
                                    )}

                                    <div className="flex flex-wrap gap-1">
                                        {challenger.tags.slice(0, 3).map(tag => (
                                            <span
                                                key={tag}
                                                className="text-[10px] px-1.5 py-0.5 bg-surface-overlay text-text-faint rounded font-mono"
                                            >
                                                {tag}
                                            </span>
                                        ))}
                                    </div>
                                </div>

                                <div className="flex-shrink-0">
                                    {isSelected ? (
                                        <div className="w-5 h-5 rounded bg-brand-500 flex items-center justify-center">
                                            <Check className="w-3 h-3 text-white" />
                                        </div>
                                    ) : (
                                        <div className="w-5 h-5 rounded border border-border" />
                                    )}
                                </div>
                            </div>
                        </DGCard>
                    );
                })}
            </div>

            <div className="mt-8 pt-5 border-t border-border flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <div className="text-sm text-text-muted">
                    <span className="text-text-primary font-medium">{selectedIds.length}</span> selected
                    {!isCountOptimal && selectedIds.length > 0 && (
                        <span className="text-status-warning ml-2 text-xs">
                            (2–4 recommended)
                        </span>
                    )}
                </div>
                <DGButton
                    variant="primary"
                    size="md"
                    disabled={selectedIds.length === 0}
                    onClick={() => onStartSimulation(selectedIds)}
                    className="sm:w-auto w-full"
                >
                    Start Demo
                    <ArrowRight className="w-3.5 h-3.5 ml-1" />
                </DGButton>
            </div>
        </div>
    );
};
