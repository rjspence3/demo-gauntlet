import React, { useEffect, useState } from 'react';
import { getSessionReport, SessionReport } from '../api/client';
import { Loader2, Trophy, RefreshCw, Star, Target, Zap, TrendingDown, Download } from 'lucide-react';
import { cn } from '../lib/utils';
import { DGCard, DGButton, DGProgress, DGBadge } from './ui';

interface SummaryViewProps {
    sessionId: string;
    onRestart: () => void;
}

export const SummaryView: React.FC<SummaryViewProps> = ({ sessionId, onRestart }) => {
    const [report, setReport] = useState<SessionReport | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchReport = async () => {
            try {
                const data = await getSessionReport(sessionId);
                setReport(data);
            } catch (err) {
                console.error(err);
            } finally {
                setLoading(false);
            }
        };
        fetchReport();
    }, [sessionId]);

    if (loading) {
        return (
            <div className="flex justify-center items-center h-64">
                <Loader2 className="w-8 h-8 text-orange-500 animate-spin" />
            </div>
        );
    }

    if (!report) {
        return (
            <div className="text-center text-rose-600">
                Failed to load report.
            </div>
        );
    }

    const getGrade = (score: number) => {
        if (score >= 90) return 'S';
        if (score >= 80) return 'A';
        if (score >= 70) return 'B';
        if (score >= 60) return 'C';
        return 'D';
    };

    const grade = getGrade(report.overall_score);

    const getScoreVariant = (score: number): 'success' | 'warning' | 'danger' => {
        if (score >= 80) return 'success';
        if (score >= 60) return 'warning';
        return 'danger';
    };

    const formatPersonaName = (personaId: string) =>
        personaId
            .split('_')
            .map(w => w.charAt(0).toUpperCase() + w.slice(1))
            .join(' ');

    const handleExport = () => {
        const blob = new Blob([JSON.stringify(report, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `gauntlet-report-${sessionId}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    };

    return (
        <div className="max-w-5xl mx-auto animate-fade-in pb-20 p-4 sm:p-6">
            <div className="text-center mb-8 sm:mb-12">
                <h2 className="text-3xl sm:text-5xl font-bold text-slate-900 mb-4">Mission Debrief</h2>
                <p className="text-slate-500 text-base sm:text-lg">Performance analysis and readiness assessment.</p>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 sm:gap-8 mb-8 sm:mb-12">
                {/* Overall Score Card — orange accent */}
                <DGCard variant="elevated" className="lg:col-span-1 p-6 sm:p-8 flex flex-col items-center justify-center relative overflow-hidden min-h-[280px] sm:min-h-[300px] border-orange-200">
                    <div className="absolute inset-0 bg-orange-50/60" />
                    <div className="absolute top-0 right-0 p-4 opacity-10">
                        <Trophy className="w-20 sm:w-24 h-20 sm:h-24 text-orange-500" />
                    </div>
                    <div className="relative z-10 text-center">
                        <div className="text-7xl sm:text-8xl font-bold text-slate-900 mb-2">{grade}</div>
                        <div className="text-orange-500 font-mono text-lg sm:text-xl mb-6 tracking-widest">RANK</div>
                        <div className="text-4xl sm:text-5xl font-bold text-slate-900 mb-2">{report.overall_score}</div>
                        <div className="text-xs text-slate-400 uppercase tracking-widest">Overall Score</div>
                    </div>
                </DGCard>

                {/* Stats & Insights */}
                <div className="lg:col-span-2 flex flex-col space-y-4 sm:space-y-6">
                    <div className="grid grid-cols-2 gap-4 sm:gap-6">
                        <DGCard variant="elevated" className="p-4 sm:p-6 flex flex-col justify-center items-center">
                            <Target className="w-6 sm:w-8 h-6 sm:h-8 text-violet-500 mb-2 sm:mb-3" />
                            <div className="text-2xl sm:text-3xl font-bold text-slate-900">{report.total_challenges}</div>
                            <div className="text-xs text-slate-500 uppercase tracking-wider text-center">Challenges Faced</div>
                        </DGCard>
                        <DGCard variant="elevated" className="p-4 sm:p-6 flex flex-col justify-center items-center">
                            <Zap className="w-6 sm:w-8 h-6 sm:h-8 text-pink-500 mb-2 sm:mb-3" />
                            <div className="text-2xl sm:text-3xl font-bold text-slate-900">
                                {report.persona_breakdown.length}
                            </div>
                            <div className="text-xs text-slate-500 uppercase tracking-wider text-center">Personas Engaged</div>
                        </DGCard>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 sm:gap-6 flex-grow">
                        {/* Strengths */}
                        <DGCard variant="elevated" className="p-4 sm:p-6 border-t-2 border-t-emerald-500">
                            <h3 className="text-sm font-bold text-emerald-600 uppercase mb-4 flex items-center tracking-wider">
                                <Star className="w-4 h-4 mr-2" />
                                Key Strengths
                            </h3>
                            <div className="space-y-2">
                                {report.strengths?.length > 0 ? (
                                    report.strengths.map((s, i) => (
                                        <div key={i} className="flex items-start space-x-2">
                                            <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 mt-2 flex-shrink-0" />
                                            <span className="text-slate-700 text-sm leading-relaxed">{s}</span>
                                        </div>
                                    ))
                                ) : (
                                    <span className="text-slate-400 text-sm italic">No specific strengths listed.</span>
                                )}
                            </div>
                        </DGCard>

                        {/* Weaknesses */}
                        <DGCard variant="elevated" className="p-4 sm:p-6 border-t-2 border-t-rose-500">
                            <h3 className="text-sm font-bold text-rose-600 uppercase mb-4 flex items-center tracking-wider">
                                <TrendingDown className="w-4 h-4 mr-2" />
                                Areas for Improvement
                            </h3>
                            <div className="space-y-2">
                                {report.weaknesses?.length > 0 ? (
                                    report.weaknesses.map((w, i) => (
                                        <div key={i} className="flex items-start space-x-2">
                                            <div className="w-1.5 h-1.5 rounded-full bg-rose-500 mt-2 flex-shrink-0" />
                                            <span className="text-slate-700 text-sm leading-relaxed">{w}</span>
                                        </div>
                                    ))
                                ) : (
                                    <span className="text-slate-400 text-sm italic">No specific weaknesses listed.</span>
                                )}
                            </div>
                        </DGCard>
                    </div>
                </div>
            </div>

            {/* Persona Breakdown */}
            <h3 className="text-xl sm:text-2xl font-bold text-slate-900 mb-4 sm:mb-6 flex items-center">
                <span className="w-1 h-6 sm:h-8 bg-orange-500 mr-3 sm:mr-4 rounded-full" />
                Persona Breakdown
            </h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6 mb-12 sm:mb-16">
                {report.persona_breakdown?.length > 0 ? (
                    report.persona_breakdown.map((p) => (
                        <DGCard key={p.persona_id} variant="elevated" className="p-4 sm:p-6 hover:shadow-md transition-all duration-300 group">
                            <div className="flex justify-between items-start mb-4 sm:mb-6">
                                <div>
                                    <h4 className="font-bold text-slate-900 text-base sm:text-lg group-hover:text-orange-500 transition-colors">
                                        {formatPersonaName(p.persona_id)}
                                    </h4>
                                    <p className="text-xs text-slate-500 mt-1">{p.total_challenges} interactions</p>
                                </div>
                                <div className={cn(
                                    "text-xl sm:text-2xl font-bold",
                                    p.average_score >= 80 ? "text-emerald-600" :
                                        p.average_score >= 60 ? "text-amber-600" : "text-rose-600"
                                )}>
                                    {Math.round(p.average_score)}
                                </div>
                            </div>

                            <div className="space-y-3">
                                <div className="flex justify-between text-xs text-slate-500 mb-1">
                                    <span>Performance</span>
                                    <span>{Math.round(p.average_score)}%</span>
                                </div>
                                <DGProgress
                                    value={p.average_score}
                                    variant={getScoreVariant(p.average_score)}
                                />
                            </div>

                            {p.component_scores && (
                                <div className="mt-4 sm:mt-6 pt-4 border-t border-slate-100 grid grid-cols-2 gap-2">
                                    {Object.entries(p.component_scores).map(([key, score]) => (
                                        <div key={key} className="flex justify-between items-center text-xs">
                                            <span className="text-slate-500 capitalize">{key}</span>
                                            <span className={cn(
                                                "font-mono",
                                                score >= 8 ? "text-emerald-600" : score >= 6 ? "text-amber-600" : "text-rose-600"
                                            )}>{score}/10</span>
                                        </div>
                                    ))}
                                </div>
                            )}
                        </DGCard>
                    ))
                ) : (
                    <DGCard variant="elevated" className="col-span-full text-center py-8">
                        <span className="text-slate-400 italic">No persona data available.</span>
                    </DGCard>
                )}
            </div>

            {/* Slide Breakdown */}
            <h3 className="text-xl sm:text-2xl font-bold text-slate-900 mb-4 sm:mb-6 flex items-center">
                <span className="w-1 h-6 sm:h-8 bg-violet-500 mr-3 sm:mr-4 rounded-full" />
                Slide Performance
            </h3>
            <DGCard variant="elevated" className="p-4 sm:p-6 mb-12 sm:mb-16">
                <div className="space-y-3">
                    {report.slide_breakdown && Object.entries(report.slide_breakdown).map(([index, score]) => (
                        <div
                            key={index}
                            className="flex flex-col sm:flex-row sm:items-center justify-between p-3 sm:p-4 rounded-xl bg-slate-50 gap-2 sm:gap-4"
                        >
                            <span className="text-slate-900 font-medium">Slide {parseInt(index) + 1}</span>
                            <div className="flex items-center gap-3 sm:gap-4">
                                <span className={cn(
                                    "font-mono font-bold",
                                    score >= 80 ? "text-emerald-600" : score >= 60 ? "text-amber-600" : "text-rose-600"
                                )}>
                                    {score}/100
                                </span>
                                <DGBadge variant={getScoreVariant(score)}>
                                    {score >= 80 ? 'Strong' : score >= 60 ? 'Average' : 'Critical'}
                                </DGBadge>
                            </div>
                        </div>
                    ))}
                    {(!report.slide_breakdown || Object.keys(report.slide_breakdown).length === 0) && (
                        <div className="py-8 text-center text-slate-400 italic">
                            No slide data available.
                        </div>
                    )}
                </div>
            </DGCard>

            <div className="flex flex-col sm:flex-row justify-center gap-3 sm:gap-4">
                <DGButton
                    variant="secondary"
                    size="lg"
                    onClick={handleExport}
                >
                    <Download className="w-5 h-5 mr-2" />
                    Export JSON
                </DGButton>
                <DGButton
                    variant="primary"
                    size="lg"
                    onClick={onRestart}
                >
                    <RefreshCw className="w-5 h-5 mr-2" />
                    Run New Simulation
                </DGButton>
            </div>
        </div>
    );
};
