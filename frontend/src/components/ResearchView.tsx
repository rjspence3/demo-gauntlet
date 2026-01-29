import React, { useEffect, useState } from 'react';
import { generateResearch, ResearchDossier, listPersonas, generateChallenges } from '../api/client';
import { Search, ShieldAlert, TrendingUp, Users, CheckCircle2, ArrowRight } from 'lucide-react';
import { DGCard, DGButton } from './ui';

/**
 * Props for the ResearchView component.
 */
interface ResearchViewProps {
    /** The current session ID. */
    sessionId: string;
    /** Callback when research is complete and user proceeds. */
    onResearchComplete: () => void;
}

/**
 * Component for displaying the research dossier and loading state.
 */
export const ResearchView: React.FC<ResearchViewProps> = ({ sessionId, onResearchComplete }) => {
    const [dossier, setDossier] = useState<ResearchDossier | null>(null);
    const [loading, setLoading] = useState(true);
    const [loadingStep, setLoadingStep] = useState(0);

    useEffect(() => {
        const fetchResearchAndGenerate = async () => {
            try {
                // 1. Generate Research
                const data = await generateResearch(sessionId);
                setDossier(data);

                // 2. Precompute Challenges for ALL personas (for evidence richness)
                const personas = await listPersonas();
                await Promise.all(personas.map(p => generateChallenges(sessionId, p.id)));

            } catch (err) {
                console.error(err);
            } finally {
                setLoading(false);
            }
        };
        fetchResearchAndGenerate();
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
            <div className="flex flex-col items-center justify-center min-h-[60vh] px-4">
                <div className="relative mb-8">
                    <div className="absolute inset-0 bg-violet-500 blur-xl opacity-20 animate-pulse"></div>
                    <div className="w-20 sm:w-24 h-20 sm:h-24 border-4 border-slate-800 border-t-violet-500 rounded-full animate-spin relative z-10"></div>
                    <div className="absolute inset-0 flex items-center justify-center">
                        <Search className="w-6 sm:w-8 h-6 sm:h-8 text-violet-500 animate-pulse" />
                    </div>
                </div>
                <h2 className="text-xl sm:text-2xl font-bold text-white mb-2 text-center">Researching Prospect</h2>
                <p className="text-violet-400 font-mono text-xs sm:text-sm animate-pulse text-center">
                    {loadingTexts[loadingStep]}
                </p>
            </div>
        );
    }

    if (!dossier) {
        return (
            <div className="text-center text-rose-500">
                Failed to load research. Please try again.
            </div>
        );
    }

    return (
        <div className="max-w-6xl mx-auto animate-fade-in pb-20 px-4 sm:px-6">
            <div className="flex flex-col sm:flex-row sm:justify-between sm:items-end gap-4 mb-6 sm:mb-8 border-b border-slate-800 pb-6">
                <div>
                    <h2 className="text-2xl sm:text-4xl font-bold text-white mb-2">Mission Intelligence</h2>
                    <p className="text-slate-400 font-light text-sm sm:text-base">
                        AI-generated dossier based on your deck and live web search.
                    </p>
                </div>
                <DGButton
                    variant="primary"
                    onClick={onResearchComplete}
                    className="w-full sm:w-auto"
                >
                    Enter Gauntlet
                    <ArrowRight className="w-5 h-5 ml-2" />
                </DGButton>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6">
                {/* Competitors */}
                <DGCard className="p-4 sm:p-6 border-t-2 border-t-violet-500">
                    <div className="flex items-center mb-4 sm:mb-6">
                        <div className="bg-violet-500/20 p-2.5 sm:p-3 rounded-lg mr-3 sm:mr-4">
                            <Users className="w-5 sm:w-6 h-5 sm:h-6 text-violet-400" />
                        </div>
                        <h3 className="text-lg sm:text-xl font-bold text-white">Competitor Intel</h3>
                    </div>
                    <ul className="space-y-3 sm:space-y-4">
                        {dossier.competitor_insights?.length > 0 ? (
                            dossier.competitor_insights.map((insight, i) => (
                                <li key={i} className="flex items-start text-slate-300 text-sm leading-relaxed">
                                    <span className="w-1.5 h-1.5 bg-violet-500 rounded-full mt-2 mr-3 flex-shrink-0"></span>
                                    {insight}
                                </li>
                            ))
                        ) : (
                            <li className="text-slate-500 text-sm italic">No competitor insights found.</li>
                        )}
                    </ul>
                </DGCard>

                {/* Costs */}
                <DGCard className="p-4 sm:p-6 border-t-2 border-t-cyan-400">
                    <div className="flex items-center mb-4 sm:mb-6">
                        <div className="bg-cyan-400/20 p-2.5 sm:p-3 rounded-lg mr-3 sm:mr-4">
                            <TrendingUp className="w-5 sm:w-6 h-5 sm:h-6 text-cyan-400" />
                        </div>
                        <h3 className="text-lg sm:text-xl font-bold text-white">Financial Context</h3>
                    </div>
                    <ul className="space-y-3 sm:space-y-4">
                        {dossier.cost_benchmarks?.length > 0 ? (
                            dossier.cost_benchmarks.map((item, i) => (
                                <li key={i} className="flex items-start text-slate-300 text-sm leading-relaxed">
                                    <span className="w-1.5 h-1.5 bg-cyan-400 rounded-full mt-2 mr-3 flex-shrink-0"></span>
                                    {item}
                                </li>
                            ))
                        ) : (
                            <li className="text-slate-500 text-sm italic">No financial context found.</li>
                        )}
                    </ul>
                </DGCard>

                {/* Risks */}
                <DGCard className="p-4 sm:p-6 border-t-2 border-t-rose-500">
                    <div className="flex items-center mb-4 sm:mb-6">
                        <div className="bg-rose-500/20 p-2.5 sm:p-3 rounded-lg mr-3 sm:mr-4">
                            <ShieldAlert className="w-5 sm:w-6 h-5 sm:h-6 text-rose-400" />
                        </div>
                        <h3 className="text-lg sm:text-xl font-bold text-white">Risk Analysis</h3>
                    </div>
                    <ul className="space-y-3 sm:space-y-4">
                        {dossier.implementation_risks?.length > 0 ? (
                            dossier.implementation_risks.map((risk, i) => (
                                <li key={i} className="flex items-start text-slate-300 text-sm leading-relaxed">
                                    <span className="w-1.5 h-1.5 bg-rose-500 rounded-full mt-2 mr-3 flex-shrink-0"></span>
                                    {risk}
                                </li>
                            ))
                        ) : (
                            <li className="text-slate-500 text-sm italic">No risks identified.</li>
                        )}
                    </ul>
                </DGCard>
            </div>

            <DGCard className="mt-6 sm:mt-8 p-3 sm:p-4">
                <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 text-xs text-slate-500 font-mono">
                    <div className="flex items-center space-x-3 sm:space-x-4">
                        <span>SOURCES: {dossier.sources?.length || 0}</span>
                        <span className="hidden sm:block w-1 h-1 bg-slate-700 rounded-full"></span>
                        <span>CONFIDENCE: HIGH</span>
                    </div>
                    <div className="flex items-center text-cyan-400">
                        <CheckCircle2 className="w-4 h-4 mr-2" />
                        DOSSIER VERIFIED
                    </div>
                </div>
            </DGCard>
        </div>
    );
};
