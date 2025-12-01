import React, { useEffect, useState } from 'react';
import { getSessionReport, SessionReport } from '../api/client';
import { Loader2, Trophy, AlertTriangle, RefreshCw, Star, Target, Zap, TrendingDown } from 'lucide-react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

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
                <Loader2 className="w-8 h-8 text-neon-blue animate-spin" />
            </div>
        );
    }

    if (!report) {
        return (
            <div className="text-center text-danger-red">
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

    return (
        <div className="max-w-5xl mx-auto animate-fade-in pb-20 p-6">
            <div className="text-center mb-12">
                <h2 className="text-5xl font-display font-bold text-white mb-4">Mission Debrief</h2>
                <p className="text-gray-400 text-lg">Performance analysis and readiness assessment.</p>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-12">
                {/* Overall Score Card */}
                <div className="lg:col-span-1 glass-panel rounded-3xl p-8 flex flex-col items-center justify-center relative overflow-hidden min-h-[300px]">
                    <div className="absolute inset-0 bg-neon-blue/5"></div>
                    <div className="absolute top-0 right-0 p-4 opacity-20">
                        <Trophy className="w-24 h-24 text-white" />
                    </div>
                    <div className="relative z-10 text-center">
                        <div className="text-8xl font-display font-bold text-white mb-2 text-glow">{grade}</div>
                        <div className="text-neon-blue font-mono text-xl mb-6 tracking-widest">RANK</div>
                        <div className="text-5xl font-bold text-white mb-2">{report.overall_score}</div>
                        <div className="text-xs text-gray-500 uppercase tracking-widest">Overall Score</div>
                    </div>
                </div>

                {/* Stats & Insights */}
                <div className="lg:col-span-2 flex flex-col space-y-6">
                    <div className="grid grid-cols-2 gap-6">
                        <div className="glass-panel p-6 rounded-2xl flex flex-col justify-center items-center bg-white/5 hover:bg-white/10 transition-colors">
                            <Target className="w-8 h-8 text-neon-purple mb-3" />
                            <div className="text-3xl font-bold text-white">{report.total_challenges}</div>
                            <div className="text-xs text-gray-500 uppercase tracking-wider">Challenges Faced</div>
                        </div>
                        <div className="glass-panel p-6 rounded-2xl flex flex-col justify-center items-center bg-white/5 hover:bg-white/10 transition-colors">
                            <Zap className="w-8 h-8 text-neon-pink mb-3" />
                            <div className="text-3xl font-bold text-white">
                                {report.persona_breakdown.length}
                            </div>
                            <div className="text-xs text-gray-500 uppercase tracking-wider">Personas Engaged</div>
                        </div>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6 flex-grow">
                        {/* Strengths */}
                        <div className="glass-panel p-6 rounded-2xl border-t-4 border-t-green-500 bg-green-500/5">
                            <h3 className="text-sm font-bold text-green-400 uppercase mb-4 flex items-center tracking-wider">
                                <Star className="w-4 h-4 mr-2" />
                                Key Strengths
                            </h3>
                            <div className="space-y-2">
                                {report.strengths?.length > 0 ? (
                                    report.strengths.map((s, i) => (
                                        <div key={i} className="flex items-start space-x-2">
                                            <div className="w-1.5 h-1.5 rounded-full bg-green-500 mt-2 flex-shrink-0"></div>
                                            <span className="text-gray-300 text-sm leading-relaxed">{s}</span>
                                        </div>
                                    ))
                                ) : (
                                    <span className="text-gray-500 text-sm italic">No specific strengths listed.</span>
                                )}
                            </div>
                        </div>

                        {/* Weaknesses */}
                        <div className="glass-panel p-6 rounded-2xl border-t-4 border-t-danger-red bg-danger-red/5">
                            <h3 className="text-sm font-bold text-danger-red uppercase mb-4 flex items-center tracking-wider">
                                <TrendingDown className="w-4 h-4 mr-2" />
                                Areas for Improvement
                            </h3>
                            <div className="space-y-2">
                                {report.weaknesses?.length > 0 ? (
                                    report.weaknesses.map((w, i) => (
                                        <div key={i} className="flex items-start space-x-2">
                                            <div className="w-1.5 h-1.5 rounded-full bg-danger-red mt-2 flex-shrink-0"></div>
                                            <span className="text-gray-300 text-sm leading-relaxed">{w}</span>
                                        </div>
                                    ))
                                ) : (
                                    <span className="text-gray-500 text-sm italic">No specific weaknesses listed.</span>
                                )}
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Persona Breakdown */}
            <h3 className="text-2xl font-display font-bold text-white mb-6 flex items-center">
                <span className="w-1 h-8 bg-neon-blue mr-4 rounded-full"></span>
                Persona Breakdown
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-16">
                {report.persona_breakdown?.length > 0 ? (
                    report.persona_breakdown.map((p) => (
                        <div key={p.persona_id} className="glass-panel p-6 rounded-2xl hover:border-white/20 transition-all duration-300 group">
                            <div className="flex justify-between items-start mb-6">
                                <div>
                                    <h4 className="font-bold text-white capitalize text-lg group-hover:text-neon-blue transition-colors">{p.persona_id.replace('_', ' ')}</h4>
                                    <p className="text-xs text-gray-500 mt-1">{p.total_challenges} interactions</p>
                                </div>
                                <div className={clsx(
                                    "text-2xl font-bold font-display",
                                    p.average_score >= 80 ? "text-green-400" :
                                        p.average_score >= 60 ? "text-yellow-400" : "text-danger-red"
                                )}>
                                    {Math.round(p.average_score)}
                                </div>
                            </div>

                            <div className="space-y-3">
                                <div className="flex justify-between text-xs text-gray-400 mb-1">
                                    <span>Performance</span>
                                    <span>{Math.round(p.average_score)}%</span>
                                </div>
                                <div className="w-full bg-gray-800 h-2 rounded-full overflow-hidden">
                                    <div
                                        className={clsx(
                                            "h-full rounded-full transition-all duration-1000",
                                            p.average_score >= 80 ? "bg-green-500" :
                                                p.average_score >= 60 ? "bg-yellow-500" : "bg-danger-red"
                                        )}
                                        style={{ width: `${p.average_score}%` }}
                                    ></div>
                                </div>
                            </div>

                            {/* Component Scores (if available) */}
                            {p.component_scores && (
                                <div className="mt-6 pt-4 border-t border-white/5 grid grid-cols-2 gap-2">
                                    {Object.entries(p.component_scores).map(([key, score]) => (
                                        <div key={key} className="flex justify-between items-center text-xs">
                                            <span className="text-gray-500 capitalize">{key}</span>
                                            <span className={clsx(
                                                "font-mono",
                                                score >= 8 ? "text-green-400" : score >= 6 ? "text-yellow-400" : "text-danger-red"
                                            )}>{score}/10</span>
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>
                    ))
                ) : (
                    <div className="col-span-3 text-center text-gray-500 italic py-8 border border-white/5 rounded-xl bg-white/5">
                        No persona data available.
                    </div>
                )}
            </div>

            <div className="flex justify-center">
                <button
                    onClick={onRestart}
                    className="flex items-center space-x-3 px-10 py-5 bg-white text-black rounded-full font-bold text-lg hover:bg-gray-200 hover:scale-105 transition-all shadow-[0_0_30px_rgba(255,255,255,0.2)]"
                >
                    <RefreshCw className="w-6 h-6" />
                    <span>RUN NEW SIMULATION</span>
                </button>
            </div>
        </div>
    );
};
