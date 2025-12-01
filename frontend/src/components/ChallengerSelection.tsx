import React, { useEffect, useState } from 'react';
import { Users, Shield, TrendingUp, AlertTriangle, ArrowRight, Check, Plus, Minus, Info } from 'lucide-react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';
import { listPersonas, ChallengerPersona } from '../api/client';

interface ChallengerSelectionProps {
    sessionId: string;
    onSelectionChanged: (personaIds: string[]) => void;
    onConfirm: () => void;
}

export const ChallengerSelection: React.FC<ChallengerSelectionProps> = ({ sessionId, onSelectionChanged, onConfirm }) => {
    const [personas, setPersonas] = useState<ChallengerPersona[]>([]);
    const [selectedIds, setSelectedIds] = useState<string[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchPersonas = async () => {
            try {
                const data = await listPersonas();
                setPersonas(data);
                // Pre-select top 2
                const initial = data.slice(0, 2).map(p => p.id);
                setSelectedIds(initial);
                onSelectionChanged(initial);
            } catch (err) {
                console.error("Failed to fetch personas", err);
            } finally {
                setLoading(false);
            }
        };
        fetchPersonas();
    }, []);

    const toggleSelection = (id: string) => {
        let newSelection;
        if (selectedIds.includes(id)) {
            newSelection = selectedIds.filter(pid => pid !== id);
        } else {
            if (selectedIds.length >= 4) return; // Max 4
            newSelection = [...selectedIds, id];
        }
        setSelectedIds(newSelection);
        onSelectionChanged(newSelection);
    };

    const getIcon = (role: string) => {
        switch (role.toLowerCase()) {
            case 'cto': return <Shield className="w-5 h-5" />;
            case 'cfo': return <TrendingUp className="w-5 h-5" />;
            case 'compliance officer': return <AlertTriangle className="w-5 h-5" />;
            default: return <Users className="w-5 h-5" />;
        }
    };

    // Mock evidence score for now (randomized for demo feel)
    const getEvidenceScore = (id: string) => {
        // Deterministic pseudo-random based on ID length
        return (id.length * 7) % 10 + 1;
    };

    const [isBriefing, setIsBriefing] = useState(false);

    const handleConfirm = async () => {
        setIsBriefing(true);
        try {
            // Call precompute endpoint
            const response = await fetch(`http://localhost:8005/research/precompute/${sessionId}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ persona_ids: selectedIds })
            });

            if (!response.ok) {
                throw new Error("Failed to precompute challenges");
            }

            onConfirm();
        } catch (err) {
            console.error("Precompute failed", err);
            // Proceed anyway? Or show error? For MVP proceed to room, maybe it works partially.
            // But better to alert.
            alert("Failed to brief challengers. Proceeding with limited context.");
            onConfirm();
        } finally {
            setIsBriefing(false);
        }
    };

    if (loading) {
        return <div className="flex items-center justify-center min-h-[50vh] text-neon-blue animate-pulse">Loading Challengers...</div>;
    }

    if (isBriefing) {
        return (
            <div className="flex flex-col items-center justify-center min-h-[80vh] w-full animate-fade-in">
                <div className="w-16 h-16 border-4 border-neon-blue border-t-transparent rounded-full animate-spin mb-6"></div>
                <h2 className="text-2xl font-bold text-white mb-2">Briefing Challengers...</h2>
                <p className="text-gray-400">They are analyzing your deck and the research dossier.</p>
            </div>
        );
    }

    const recommended = personas.slice(0, 3);
    const others = personas.slice(3);

    const renderRow = (persona: ChallengerPersona) => {
        const isSelected = selectedIds.includes(persona.id);
        const score = getEvidenceScore(persona.id);

        return (
            <div key={persona.id} className={twMerge(
                "flex items-center justify-between p-4 rounded-xl border transition-all duration-200 mb-3",
                isSelected
                    ? "bg-neon-blue/10 border-neon-blue shadow-[0_0_10px_rgba(0,243,255,0.1)]"
                    : "bg-white/5 border-white/10 hover:bg-white/10"
            )}>
                <div className="flex items-center space-x-4 flex-1">
                    <div className={twMerge(
                        "w-10 h-10 rounded-lg flex items-center justify-center",
                        isSelected ? "bg-neon-blue text-black" : "bg-white/10 text-gray-400"
                    )}>
                        {getIcon(persona.role)}
                    </div>
                    <div>
                        <h3 className="font-bold text-white">{persona.name}</h3>
                        <p className="text-xs text-gray-400">{persona.role}</p>
                    </div>
                </div>

                <div className="flex items-center space-x-8 flex-1">
                    <div className="flex flex-col w-32">
                        <span className="text-xs text-gray-500 mb-1">Evidence</span>
                        <div className="h-1.5 w-full bg-gray-800 rounded-full overflow-hidden">
                            <div
                                className="h-full bg-neon-blue"
                                style={{ width: `${score * 10}%` }}
                            ></div>
                        </div>
                    </div>

                    <div className="flex flex-wrap gap-2">
                        {persona.focus_areas.slice(0, 2).map(area => (
                            <span key={area} className="text-xs px-2 py-0.5 rounded bg-white/5 text-gray-300 border border-white/5">
                                {area}
                            </span>
                        ))}
                    </div>
                </div>

                <div className="flex items-center space-x-3">
                    <button className="p-2 text-gray-400 hover:text-white transition-colors">
                        <Info className="w-5 h-5" />
                    </button>
                    <button
                        onClick={() => toggleSelection(persona.id)}
                        className={twMerge(
                            "flex items-center space-x-2 px-4 py-2 rounded-lg text-sm font-bold transition-all",
                            isSelected
                                ? "bg-neon-blue text-black hover:bg-neon-blue/80"
                                : "bg-white/10 text-white hover:bg-white/20"
                        )}
                    >
                        {isSelected ? (
                            <>
                                <Check className="w-4 h-4" />
                                <span>Selected</span>
                            </>
                        ) : (
                            <>
                                <Plus className="w-4 h-4" />
                                <span>Add</span>
                            </>
                        )}
                    </button>
                </div>
            </div>
        );
    };

    return (
        <div className="flex flex-col items-center min-h-[80vh] w-full max-w-5xl mx-auto p-6 animate-fade-in">
            <div className="text-center mb-10">
                <h2 className="text-4xl font-display font-bold mb-4 text-white">Choose Your Challengers</h2>
                <p className="text-gray-400 text-lg max-w-2xl mx-auto">
                    Select up to 4 personas to join the room. We've recommended the ones with the most relevant evidence.
                </p>
            </div>

            <div className="w-full mb-8">
                <h3 className="text-sm font-bold text-neon-blue uppercase tracking-wider mb-4">Recommended</h3>
                <div className="space-y-2">
                    {recommended.map(renderRow)}
                </div>
            </div>

            {others.length > 0 && (
                <div className="w-full mb-12">
                    <h3 className="text-sm font-bold text-gray-500 uppercase tracking-wider mb-4">All Challengers</h3>
                    <div className="space-y-2">
                        {others.map(renderRow)}
                    </div>
                </div>
            )}

            <button
                onClick={handleConfirm}
                disabled={selectedIds.length === 0}
                className={twMerge(
                    "fixed bottom-8 right-8 flex items-center space-x-3 px-8 py-4 rounded-full font-bold text-lg transition-all duration-300 shadow-lg z-50",
                    selectedIds.length > 0
                        ? "bg-neon-blue text-black hover:shadow-[0_0_30px_rgba(0,243,255,0.4)] hover:scale-105"
                        : "bg-gray-800 text-gray-500 cursor-not-allowed"
                )}
            >
                <span>Start Simulation ({selectedIds.length})</span>
                <ArrowRight className="w-5 h-5" />
            </button>
        </div>
    );
};
