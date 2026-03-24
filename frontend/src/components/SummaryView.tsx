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
                <Loader2 className="w-6 h-6 text-ai-500 animate-spin" />
            </div>
        );
    }

    if (!report) {
        return (
            <div className="text-center text-status-error text-sm mt-20">
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
        <div className="max-w-4xl mx-auto animate-fade-in pb-20 px-4 sm:px-6">
            {/* Header — Pitch confidence */}
            <div className="text-center mb-10">
                <h2 className="text-3xl sm:text-4xl font-bold text-text-primary mb-2 tracking-tight">Session Report</h2>
                <p className="text-text-muted text-sm">Performance analysis and readiness assessment</p>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 mb-10">
                {/* Overall Score Card — glassmorphism with ai accent */}
                <DGCard className="lg:col-span-1 p-6 flex flex-col items-center justify-center relative overflow-hidden min-h-[240px] border-ai-300/30">
                    <div className="absolute top-0 right-0 p-4 opacity-5">
                        <Trophy className="w-20 h-20 text-ai-500" />
                    </div>
                    <div className="relative z-10 text-center">
                        <div className="text-6xl font-extrabold text-text-primary mb-1">{grade}</div>
                        <div className="text-ai-500 text-xs font-mono mb-5 uppercase tracking-widest">Rank</div>
                        <div className="text-4xl font-bold text-text-primary mb-1 tabular-nums">{report.overall_score}</div>
                        <div className="text-[10px] text-text-faint uppercase tracking-widest">Overall Score</div>
                    </div>
                </DGCard>

                {/* Stats & Insights */}
                <div className="lg:col-span-2 flex flex-col gap-4">
                    <div className="grid grid-cols-2 gap-4">
                        <DGCard className="p-5 flex flex-col justify-center items-center">
                            <Target className="w-5 h-5 text-ai-500 mb-2" />
                            <div className="text-2xl font-bold text-text-primary tabular-nums">{report.total_challenges}</div>
                            <div className="text-[10px] text-text-faint uppercase tracking-wider text-center">Challenges</div>
                        </DGCard>
                        <DGCard className="p-5 flex flex-col justify-center items-center">
                            <Zap className="w-5 h-5 text-brand-500 mb-2" />
                            <div className="text-2xl font-bold text-text-primary tabular-nums">
                                {report.persona_breakdown.length}
                            </div>
                            <div className="text-[10px] text-text-faint uppercase tracking-wider text-center">Personas</div>
                        </DGCard>
                    </div>

                    {/* Strengths / Weaknesses — glassmorphism cards with accent borders */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 flex-grow">
                        <DGCard className="p-4 border-l-2 border-l-status-success">
                            <h3 className="text-xs font-semibold text-status-success uppercase mb-3 flex items-center tracking-wider">
                                <Star className="w-3.5 h-3.5 mr-1.5" />
                                What Landed
                            </h3>
                            <div className="space-y-2">
                                {report.strengths?.length > 0 ? (
                                    report.strengths.map((s, i) => (
                                        <div key={i} className="flex items-start gap-2">
                                            <div className="w-1 h-1 rounded-full bg-status-success mt-2 flex-shrink-0" />
                                            <span className="text-text-secondary text-sm leading-relaxed">{s}</span>
                                        </div>
                                    ))
                                ) : (
                                    <span className="text-text-faint text-sm">No specific strengths listed.</span>
                                )}
                            </div>
                        </DGCard>

                        <DGCard className="p-4 border-l-2 border-l-brand-500">
                            <h3 className="text-xs font-semibold text-brand-500 uppercase mb-3 flex items-center tracking-wider">
                                <TrendingDown className="w-3.5 h-3.5 mr-1.5" />
                                What to Sharpen
                            </h3>
                            <div className="space-y-2">
                                {report.weaknesses?.length > 0 ? (
                                    report.weaknesses.map((w, i) => (
                                        <div key={i} className="flex items-start gap-2">
                                            <div className="w-1 h-1 rounded-full bg-brand-500 mt-2 flex-shrink-0" />
                                            <span className="text-text-secondary text-sm leading-relaxed">{w}</span>
                                        </div>
                                    ))
                                ) : (
                                    <span className="text-text-faint text-sm">No specific weaknesses listed.</span>
                                )}
                            </div>
                        </DGCard>
                    </div>
                </div>
            </div>

            {/* Persona Breakdown */}
            <h3 className="text-lg font-bold text-text-primary mb-4 flex items-center tracking-tight">
                <span className="w-1 h-5 bg-gradient-to-b from-ai-500 to-ai-400 mr-3 rounded-full" />
                Persona Breakdown
            </h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 mb-10">
                {report.persona_breakdown?.length > 0 ? (
                    report.persona_breakdown.map((p) => (
                        <DGCard key={p.persona_id} className="p-4 hover:shadow-glass-hover transition-all group">
                            <div className="flex justify-between items-start mb-4">
                                <div>
                                    <h4 className="font-semibold text-text-primary text-sm group-hover:text-ai-600 transition-colors">
                                        {formatPersonaName(p.persona_id)}
                                    </h4>
                                    <p className="text-xs text-text-faint mt-0.5">{p.total_challenges} interactions</p>
                                </div>
                                <div className={cn(
                                    "text-xl font-bold tabular-nums",
                                    p.average_score >= 80 ? "text-status-success" :
                                        p.average_score >= 60 ? "text-status-warning" : "text-status-error"
                                )}>
                                    {Math.round(p.average_score)}
                                </div>
                            </div>

                            <div className="space-y-2">
                                <div className="flex justify-between text-[10px] text-text-faint mb-1">
                                    <span>Performance</span>
                                    <span className="tabular-nums">{Math.round(p.average_score)}%</span>
                                </div>
                                <DGProgress
                                    value={p.average_score}
                                    variant={getScoreVariant(p.average_score)}
                                />
                            </div>

                            {p.component_scores && (
                                <div className="mt-4 pt-3 border-t border-border grid grid-cols-2 gap-1.5">
                                    {Object.entries(p.component_scores).map(([key, score]) => (
                                        <div key={key} className="flex justify-between items-center text-xs">
                                            <span className="text-text-faint capitalize">{key}</span>
                                            <span className={cn(
                                                "font-mono tabular-nums",
                                                score >= 8 ? "text-status-success" : score >= 6 ? "text-status-warning" : "text-status-error"
                                            )}>{score}/10</span>
                                        </div>
                                    ))}
                                </div>
                            )}
                        </DGCard>
                    ))
                ) : (
                    <DGCard className="col-span-full text-center py-8">
                        <span className="text-text-faint text-sm">No persona data available.</span>
                    </DGCard>
                )}
            </div>

            {/* Slide Breakdown */}
            <h3 className="text-lg font-bold text-text-primary mb-4 flex items-center tracking-tight">
                <span className="w-1 h-5 bg-gradient-to-b from-ai-500 to-ai-400 mr-3 rounded-full" />
                Slide Performance
            </h3>
            <DGCard className="p-4 mb-10">
                <div className="space-y-2">
                    {report.slide_breakdown && Object.entries(report.slide_breakdown).map(([index, score]) => (
                        <div
                            key={index}
                            className="flex items-center justify-between p-3 rounded-xl bg-white/40 border border-border gap-3"
                        >
                            <span className="text-text-primary text-sm font-semibold">Slide {parseInt(index) + 1}</span>
                            <div className="flex items-center gap-3">
                                <span className={cn(
                                    "font-mono text-sm font-medium tabular-nums",
                                    score >= 80 ? "text-status-success" : score >= 60 ? "text-status-warning" : "text-status-error"
                                )}>
                                    {score}
                                </span>
                                <DGBadge variant={getScoreVariant(score)}>
                                    {score >= 80 ? 'Strong' : score >= 60 ? 'Average' : 'Weak'}
                                </DGBadge>
                            </div>
                        </div>
                    ))}
                    {(!report.slide_breakdown || Object.keys(report.slide_breakdown).length === 0) && (
                        <div className="py-8 text-center text-text-faint text-sm">
                            No slide data available.
                        </div>
                    )}
                </div>
            </DGCard>

            <div className="flex flex-col sm:flex-row justify-center gap-3">
                <DGButton variant="secondary" size="md" onClick={handleExport}>
                    <Download className="w-4 h-4 mr-1.5" />
                    Export JSON
                </DGButton>
                <DGButton variant="primary" size="md" onClick={onRestart}>
                    <RefreshCw className="w-4 h-4 mr-1.5" />
                    New Simulation
                </DGButton>
            </div>
        </div>
    );
};
