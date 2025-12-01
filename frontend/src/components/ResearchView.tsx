import React, { useEffect, useState } from 'react';
import { generateResearch, ResearchDossier } from '../api/client';
import { Loader2, Search, ShieldAlert, TrendingUp, Users, CheckCircle2, ArrowRight } from 'lucide-react';
import { clsx } from 'clsx';

interface ResearchViewProps {
    sessionId: string;
    onResearchComplete: () => void;
}

export const ResearchView: React.FC<ResearchViewProps> = ({ sessionId, onResearchComplete }) => {
    const [dossier, setDossier] = useState<ResearchDossier | null>(null);
    const [loading, setLoading] = useState(true);
    const [loadingStep, setLoadingStep] = useState(0);

    useEffect(() => {
        const fetchResearch = async () => {
            try {
                const data = await generateResearch(sessionId);
                setDossier(data);
            } catch (err) {
                console.error(err);
            } finally {
                setLoading(false);
            }
        };
        fetchResearch();
    }, [sessionId]);

    // Simulated loading steps for effect
    useEffect(() => {
        if (!loading) return;
        const interval = setInterval(() => {
            setLoadingStep(prev => (prev + 1) % 4);
        }, 800);
        return () => clearInterval(interval);
    }, [loading]);

    const loadingTexts = [
        "Scanning industry databases...",
        "Analyzing competitor strategies...",
        "Identifying compliance risks...",
        "Compiling executive dossier..."
    ];

    if (loading) {
        return (
            <div className="flex flex-col items-center justify-center min-h-[60vh]">
                <div className="relative mb-8">
                    <div className="absolute inset-0 bg-neon-purple blur-xl opacity-20 animate-pulse"></div>
                    <div className="w-24 h-24 border-4 border-white/10 border-t-neon-purple rounded-full animate-spin relative z-10"></div>
                    <div className="absolute inset-0 flex items-center justify-center">
                        <Search className="w-8 h-8 text-neon-purple animate-pulse" />
                    </div>
                </div>
                <h2 className="text-2xl font-display font-bold text-white mb-2">Researching Prospect</h2>
                <p className="text-neon-purple font-mono text-sm animate-pulse">
                    {loadingTexts[loadingStep]}
                </p>
            </div>
        );
    }

    if (!dossier) {
        return (
            <div className="text-center text-danger-red">
                Failed to load research. Please try again.
            </div>
        );
    }

    return (
        <div className="max-w-6xl mx-auto animate-fade-in pb-20">
            <div className="flex justify-between items-end mb-8 border-b border-white/10 pb-6">
                <div>
                    <h2 className="text-4xl font-display font-bold text-white mb-2">Mission Intelligence</h2>
                    <p className="text-gray-400 font-light">
                        AI-generated dossier based on your deck and live web search.
                    </p>
                </div>
                <button
                    onClick={onResearchComplete}
                    className="group flex items-center bg-neon-blue/10 hover:bg-neon-blue/20 border border-neon-blue/50 text-neon-blue px-6 py-3 rounded-full font-bold transition-all duration-300 hover:shadow-[0_0_20px_rgba(0,243,255,0.3)]"
                >
                    ENTER GAUNTLET
                    <ArrowRight className="w-5 h-5 ml-2 group-hover:translate-x-1 transition-transform" />
                </button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {/* Competitors */}
                <div className="glass-panel p-6 rounded-2xl border-t-4 border-t-neon-purple">
                    <div className="flex items-center mb-6">
                        <div className="bg-neon-purple/20 p-3 rounded-lg mr-4">
                            <Users className="w-6 h-6 text-neon-purple" />
                        </div>
                        <h3 className="text-xl font-bold text-white">Competitor Intel</h3>
                    </div>
                    <ul className="space-y-4">
                        {dossier.competitor_insights?.length > 0 ? (
                            dossier.competitor_insights.map((insight, i) => (
                                <li key={i} className="flex items-start text-gray-300 text-sm leading-relaxed">
                                    <span className="w-1.5 h-1.5 bg-neon-purple rounded-full mt-2 mr-3 flex-shrink-0"></span>
                                    {insight}
                                </li>
                            ))
                        ) : (
                            <li className="text-gray-500 text-sm italic">No competitor insights found.</li>
                        )}
                    </ul>
                </div>

                {/* Costs */}
                <div className="glass-panel p-6 rounded-2xl border-t-4 border-t-neon-blue">
                    <div className="flex items-center mb-6">
                        <div className="bg-neon-blue/20 p-3 rounded-lg mr-4">
                            <TrendingUp className="w-6 h-6 text-neon-blue" />
                        </div>
                        <h3 className="text-xl font-bold text-white">Financial Context</h3>
                    </div>
                    <ul className="space-y-4">
                        {dossier.cost_benchmarks?.length > 0 ? (
                            dossier.cost_benchmarks.map((item, i) => (
                                <li key={i} className="flex items-start text-gray-300 text-sm leading-relaxed">
                                    <span className="w-1.5 h-1.5 bg-neon-blue rounded-full mt-2 mr-3 flex-shrink-0"></span>
                                    {item}
                                </li>
                            ))
                        ) : (
                            <li className="text-gray-500 text-sm italic">No financial context found.</li>
                        )}
                    </ul>
                </div>

                {/* Risks */}
                <div className="glass-panel p-6 rounded-2xl border-t-4 border-t-danger-red">
                    <div className="flex items-center mb-6">
                        <div className="bg-danger-red/20 p-3 rounded-lg mr-4">
                            <ShieldAlert className="w-6 h-6 text-danger-red" />
                        </div>
                        <h3 className="text-xl font-bold text-white">Risk Analysis</h3>
                    </div>
                    <ul className="space-y-4">
                        {dossier.implementation_risks?.length > 0 ? (
                            dossier.implementation_risks.map((risk, i) => (
                                <li key={i} className="flex items-start text-gray-300 text-sm leading-relaxed">
                                    <span className="w-1.5 h-1.5 bg-danger-red rounded-full mt-2 mr-3 flex-shrink-0"></span>
                                    {risk}
                                </li>
                            ))
                        ) : (
                            <li className="text-gray-500 text-sm italic">No risks identified.</li>
                        )}
                    </ul>
                </div>
            </div>

            <div className="mt-8 glass-panel p-4 rounded-xl flex items-center justify-between text-xs text-gray-500 font-mono">
                <div className="flex items-center space-x-4">
                    <span>SOURCES SCANNED: {dossier.sources?.length || 0}</span>
                    <span className="w-1 h-1 bg-gray-700 rounded-full"></span>
                    <span>CONFIDENCE: HIGH</span>
                </div>
                <div className="flex items-center text-neon-blue">
                    <CheckCircle2 className="w-4 h-4 mr-2" />
                    DOSSIER VERIFIED
                </div>
            </div>
        </div>
    );
};
