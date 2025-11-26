import React, { useEffect, useState } from 'react';
import { generateResearch, ResearchDossier } from '../api/client';
import { Loader2, ShieldAlert, TrendingUp, DollarSign, Search, ArrowRight } from 'lucide-react';
import { clsx } from 'clsx';

interface ResearchViewProps {
    sessionId: string;
    onResearchComplete: () => void;
}

export const ResearchView: React.FC<ResearchViewProps> = ({ sessionId, onResearchComplete }) => {
    const [dossier, setDossier] = useState<ResearchDossier | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchResearch = async () => {
            try {
                const data = await generateResearch(sessionId);
                setDossier(data);
            } catch (err) {
                console.error(err);
                setError('Failed to generate research. Please try again.');
            } finally {
                setLoading(false);
            }
        };

        fetchResearch();
    }, [sessionId]);

    if (loading) {
        return (
            <div className="flex flex-col items-center justify-center min-h-[60vh]">
                <Loader2 className="w-12 h-12 text-purple-500 animate-spin mb-6" />
                <h2 className="text-2xl font-bold text-gray-200 mb-2">Conducting Deep Research</h2>
                <p className="text-gray-400 animate-pulse">Analyzing competitors, costs, and risks...</p>
            </div>
        );
    }

    if (error) {
        return (
            <div className="flex flex-col items-center justify-center min-h-[60vh] text-red-400">
                <ShieldAlert className="w-16 h-16 mb-4" />
                <p className="text-xl">{error}</p>
                <button
                    onClick={() => window.location.reload()}
                    className="mt-4 px-4 py-2 bg-gray-800 rounded hover:bg-gray-700 text-white"
                >
                    Retry
                </button>
            </div>
        );
    }

    if (!dossier) return null;

    return (
        <div className="w-full max-w-4xl mx-auto p-6 animate-in fade-in slide-in-from-bottom-4 duration-700">
            <div className="flex justify-between items-center mb-8">
                <div>
                    <h2 className="text-3xl font-bold text-white mb-2">Research Dossier</h2>
                    <p className="text-gray-400">AI-generated insights for your session.</p>
                </div>
                <button
                    onClick={onResearchComplete}
                    className="flex items-center px-6 py-3 bg-blue-600 hover:bg-blue-500 text-white rounded-lg font-semibold transition-all shadow-lg shadow-blue-500/20"
                >
                    Enter Gauntlet <ArrowRight className="ml-2 w-5 h-5" />
                </button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Competitors */}
                <div className="bg-gray-800/50 border border-gray-700 rounded-xl p-6">
                    <div className="flex items-center mb-4 text-orange-400">
                        <TrendingUp className="w-6 h-6 mr-2" />
                        <h3 className="text-xl font-semibold">Competitor Insights</h3>
                    </div>
                    <ul className="space-y-3">
                        {dossier.competitor_insights.map((item, i) => (
                            <li key={i} className="flex items-start text-gray-300 text-sm">
                                <span className="mr-2 text-orange-500/50">•</span>
                                {item}
                            </li>
                        ))}
                    </ul>
                </div>

                {/* Costs */}
                <div className="bg-gray-800/50 border border-gray-700 rounded-xl p-6">
                    <div className="flex items-center mb-4 text-green-400">
                        <DollarSign className="w-6 h-6 mr-2" />
                        <h3 className="text-xl font-semibold">Cost Benchmarks</h3>
                    </div>
                    <ul className="space-y-3">
                        {dossier.cost_benchmarks.map((item, i) => (
                            <li key={i} className="flex items-start text-gray-300 text-sm">
                                <span className="mr-2 text-green-500/50">•</span>
                                {item}
                            </li>
                        ))}
                    </ul>
                </div>

                {/* Risks */}
                <div className="bg-gray-800/50 border border-gray-700 rounded-xl p-6">
                    <div className="flex items-center mb-4 text-red-400">
                        <ShieldAlert className="w-6 h-6 mr-2" />
                        <h3 className="text-xl font-semibold">Implementation Risks</h3>
                    </div>
                    <ul className="space-y-3">
                        {dossier.implementation_risks.map((item, i) => (
                            <li key={i} className="flex items-start text-gray-300 text-sm">
                                <span className="mr-2 text-red-500/50">•</span>
                                {item}
                            </li>
                        ))}
                    </ul>
                </div>

                {/* Compliance */}
                <div className="bg-gray-800/50 border border-gray-700 rounded-xl p-6">
                    <div className="flex items-center mb-4 text-blue-400">
                        <Search className="w-6 h-6 mr-2" />
                        <h3 className="text-xl font-semibold">Compliance Notes</h3>
                    </div>
                    <ul className="space-y-3">
                        {dossier.compliance_notes.map((item, i) => (
                            <li key={i} className="flex items-start text-gray-300 text-sm">
                                <span className="mr-2 text-blue-500/50">•</span>
                                {item}
                            </li>
                        ))}
                    </ul>
                </div>
            </div>
        </div>
    );
};
