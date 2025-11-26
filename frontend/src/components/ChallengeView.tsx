import React, { useEffect, useState } from 'react';
import { listPersonas, generateChallenges, ChallengerPersona, Challenge } from '../api/client';
import { Loader2, User, MessageSquare, AlertTriangle, RefreshCw } from 'lucide-react';
import { clsx } from 'clsx';

interface ChallengeViewProps {
    sessionId: string;
}

export const ChallengeView: React.FC<ChallengeViewProps> = ({ sessionId }) => {
    const [personas, setPersonas] = useState<ChallengerPersona[]>([]);
    const [selectedPersona, setSelectedPersona] = useState<string | null>(null);
    const [challenges, setChallenges] = useState<Challenge[]>([]);
    const [loadingPersonas, setLoadingPersonas] = useState(true);
    const [generating, setGenerating] = useState(false);

    useEffect(() => {
        const fetchPersonas = async () => {
            try {
                const data = await listPersonas();
                setPersonas(data);
                if (data.length > 0) setSelectedPersona(data[0].id);
            } catch (err) {
                console.error(err);
            } finally {
                setLoadingPersonas(false);
            }
        };
        fetchPersonas();
    }, []);

    const handleGenerate = async () => {
        if (!selectedPersona) return;
        setGenerating(true);
        try {
            const data = await generateChallenges(sessionId, selectedPersona);
            setChallenges(data);
        } catch (err) {
            console.error(err);
        } finally {
            setGenerating(false);
        }
    };

    if (loadingPersonas) {
        return (
            <div className="flex justify-center items-center h-64">
                <Loader2 className="w-8 h-8 text-blue-500 animate-spin" />
            </div>
        );
    }

    return (
        <div className="w-full max-w-5xl mx-auto p-6 animate-in fade-in duration-500">
            <h2 className="text-3xl font-bold text-white mb-8 text-center">The Gauntlet</h2>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* Persona Selection */}
                <div className="lg:col-span-1 space-y-4">
                    <h3 className="text-lg font-semibold text-gray-300 mb-4">Select Challenger</h3>
                    <div className="space-y-3">
                        {personas.map((p) => (
                            <button
                                key={p.id}
                                onClick={() => setSelectedPersona(p.id)}
                                className={clsx(
                                    "w-full text-left p-4 rounded-xl border transition-all duration-200",
                                    selectedPersona === p.id
                                        ? "bg-blue-600/20 border-blue-500 shadow-[0_0_15px_rgba(59,130,246,0.3)]"
                                        : "bg-gray-800/50 border-gray-700 hover:border-gray-500 hover:bg-gray-800"
                                )}
                            >
                                <div className="flex items-center justify-between mb-1">
                                    <span className={clsx(
                                        "font-bold",
                                        selectedPersona === p.id ? "text-blue-400" : "text-gray-200"
                                    )}>{p.name}</span>
                                    {selectedPersona === p.id && <User className="w-4 h-4 text-blue-400" />}
                                </div>
                                <p className="text-xs text-gray-400 mb-2">{p.role}</p>
                                <div className="flex flex-wrap gap-1">
                                    {p.focus_areas.slice(0, 2).map((area, i) => (
                                        <span key={i} className="text-[10px] px-2 py-0.5 rounded-full bg-gray-700 text-gray-300">
                                            {area}
                                        </span>
                                    ))}
                                </div>
                            </button>
                        ))}
                    </div>

                    <button
                        onClick={handleGenerate}
                        disabled={generating || !selectedPersona}
                        className="w-full mt-6 py-3 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-500 hover:to-purple-500 text-white rounded-lg font-bold shadow-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
                    >
                        {generating ? (
                            <>
                                <Loader2 className="w-5 h-5 animate-spin mr-2" />
                                Challenging...
                            </>
                        ) : (
                            <>
                                <MessageSquare className="w-5 h-5 mr-2" />
                                Generate Challenges
                            </>
                        )}
                    </button>
                </div>

                {/* Challenge Display */}
                <div className="lg:col-span-2">
                    <h3 className="text-lg font-semibold text-gray-300 mb-4">Challenges</h3>

                    {challenges.length === 0 ? (
                        <div className="h-full min-h-[400px] flex flex-col items-center justify-center bg-gray-800/20 border-2 border-dashed border-gray-700 rounded-2xl p-8 text-center text-gray-500">
                            <User className="w-16 h-16 mb-4 opacity-20" />
                            <p className="text-lg">Select a persona and generate challenges to begin.</p>
                        </div>
                    ) : (
                        <div className="space-y-6">
                            {challenges.map((c) => (
                                <div key={c.id} className="bg-gray-800/80 border border-gray-700 rounded-xl p-6 shadow-xl animate-in slide-in-from-right-4 duration-500">
                                    <div className="flex items-start justify-between mb-4">
                                        <div className="flex items-center space-x-2">
                                            <span className={clsx(
                                                "px-2 py-1 rounded text-xs font-bold uppercase tracking-wider",
                                                c.difficulty === 'hard' ? "bg-red-500/20 text-red-400 border border-red-500/30" :
                                                    c.difficulty === 'medium' ? "bg-yellow-500/20 text-yellow-400 border border-yellow-500/30" :
                                                        "bg-green-500/20 text-green-400 border border-green-500/30"
                                            )}>
                                                {c.difficulty}
                                            </span>
                                            <span className="text-xs text-gray-500 bg-gray-900 px-2 py-1 rounded">
                                                Source: {c.context_source || "General Context"}
                                            </span>
                                        </div>
                                    </div>

                                    <p className="text-lg text-gray-100 font-medium leading-relaxed mb-4">
                                        "{c.question}"
                                    </p>

                                    <div className="flex justify-end">
                                        <button className="text-sm text-blue-400 hover:text-blue-300 flex items-center transition-colors">
                                            <RefreshCw className="w-4 h-4 mr-1" />
                                            Regenerate
                                        </button>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};
