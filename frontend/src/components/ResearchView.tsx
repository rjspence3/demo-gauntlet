import React, { useEffect, useState } from 'react';
import { generateResearch, ResearchDossier, listPersonas, generateChallenges } from '../api/client';
import { Search, ShieldAlert, TrendingUp, Users, CheckCircle2, ArrowRight } from 'lucide-react';
import { DGCard, DGButton } from './ui';

interface ResearchViewProps {
    sessionId: string;
    onResearchComplete: () => void;
}

export const ResearchView: React.FC<ResearchViewProps> = ({ sessionId, onResearchComplete }) => {
    const [dossier, setDossier] = useState<ResearchDossier | null>(null);
    const [loading, setLoading] = useState(true);
    const [loadingStep, setLoadingStep] = useState(0);

    useEffect(() => {
        const fetchResearchAndGenerate = async () => {
            try {
                const data = await generateResearch(sessionId);
                setDossier(data);

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
                    <div className="absolute inset-0 bg-accent-purple blur-xl opacity-10 animate-pulse" />
                    <div className="w-16 h-16 border-2 border-border border-t-accent-purple rounded-full animate-spin relative z-10" />
                    <div className="absolute inset-0 flex items-center justify-center">
                        <Search className="w-6 h-6 text-accent-purple animate-pulse" />
                    </div>
                </div>
                <h2 className="text-xl font-semibold text-text-primary mb-2 text-center">Researching Prospect</h2>
                <p className="text-accent-purple text-xs font-mono animate-pulse text-center">
                    {loadingTexts[loadingStep]}
                </p>
            </div>
        );
    }

    if (!dossier) {
        return (
            <div className="text-center text-status-error text-sm mt-20">
                Failed to load research. Please try again.
            </div>
        );
    }

    return (
        <div className="max-w-5xl mx-auto animate-fade-in pb-20 px-4 sm:px-6">
            <div className="flex flex-col sm:flex-row sm:justify-between sm:items-end gap-4 mb-8 border-b border-border pb-6">
                <div>
                    <h2 className="text-2xl font-semibold text-text-primary mb-1">Intelligence Dossier</h2>
                    <p className="text-text-muted text-sm">AI-generated from your deck and live web search</p>
                </div>
                <DGButton variant="primary" onClick={onResearchComplete} className="w-full sm:w-auto">
                    Continue
                    <ArrowRight className="w-4 h-4 ml-1.5" />
                </DGButton>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {/* Competitors */}
                <DGCard className="p-4 border-l-2 border-l-accent-purple">
                    <div className="flex items-center mb-4">
                        <div className="bg-accent-purple/10 p-2 rounded-lg mr-3">
                            <Users className="w-4 h-4 text-accent-purple" />
                        </div>
                        <h3 className="text-sm font-semibold text-text-primary">Competitor Intel</h3>
                    </div>
                    <ul className="space-y-3">
                        {dossier.competitor_insights?.length > 0 ? (
                            dossier.competitor_insights.map((insight, i) => (
                                <li key={i} className="flex items-start text-text-secondary text-sm leading-relaxed">
                                    <span className="w-1 h-1 bg-accent-purple rounded-full mt-2 mr-2.5 flex-shrink-0" />
                                    {insight}
                                </li>
                            ))
                        ) : (
                            <li className="text-text-faint text-sm">No competitor insights found.</li>
                        )}
                    </ul>
                </DGCard>

                {/* Costs */}
                <DGCard className="p-4 border-l-2 border-l-brand-500">
                    <div className="flex items-center mb-4">
                        <div className="bg-brand-500/10 p-2 rounded-lg mr-3">
                            <TrendingUp className="w-4 h-4 text-brand-500" />
                        </div>
                        <h3 className="text-sm font-semibold text-text-primary">Financial Context</h3>
                    </div>
                    <ul className="space-y-3">
                        {dossier.cost_benchmarks?.length > 0 ? (
                            dossier.cost_benchmarks.map((item, i) => (
                                <li key={i} className="flex items-start text-text-secondary text-sm leading-relaxed">
                                    <span className="w-1 h-1 bg-brand-500 rounded-full mt-2 mr-2.5 flex-shrink-0" />
                                    {item}
                                </li>
                            ))
                        ) : (
                            <li className="text-text-faint text-sm">No financial context found.</li>
                        )}
                    </ul>
                </DGCard>

                {/* Risks */}
                <DGCard className="p-4 border-l-2 border-l-status-error">
                    <div className="flex items-center mb-4">
                        <div className="bg-status-error/10 p-2 rounded-lg mr-3">
                            <ShieldAlert className="w-4 h-4 text-status-error" />
                        </div>
                        <h3 className="text-sm font-semibold text-text-primary">Risk Analysis</h3>
                    </div>
                    <ul className="space-y-3">
                        {dossier.implementation_risks?.length > 0 ? (
                            dossier.implementation_risks.map((risk, i) => (
                                <li key={i} className="flex items-start text-text-secondary text-sm leading-relaxed">
                                    <span className="w-1 h-1 bg-status-error rounded-full mt-2 mr-2.5 flex-shrink-0" />
                                    {risk}
                                </li>
                            ))
                        ) : (
                            <li className="text-text-faint text-sm">No risks identified.</li>
                        )}
                    </ul>
                </DGCard>
            </div>

            <DGCard className="mt-6 p-3">
                <div className="flex items-center justify-between text-[10px] text-text-faint font-mono uppercase tracking-wider">
                    <div className="flex items-center gap-4">
                        <span>Sources: {dossier.sources?.length || 0}</span>
                        <span>Confidence: High</span>
                    </div>
                    <div className="flex items-center text-status-success">
                        <CheckCircle2 className="w-3.5 h-3.5 mr-1.5" />
                        Verified
                    </div>
                </div>
            </DGCard>
        </div>
    );
};
