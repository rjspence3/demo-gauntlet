import React, { useEffect, useState } from 'react';
import { getSessionReport, SessionReport } from '../api/client';
import { Loader2, Trophy, AlertTriangle, CheckCircle, RefreshCw } from 'lucide-react';
import { clsx } from 'clsx';

interface SummaryViewProps {
    sessionId: string;
    onRestart: () => void;
}

export const SummaryView: React.FC<SummaryViewProps> = ({ sessionId, onRestart }) => {
    const [report, setReport] = useState<SessionReport | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const loadReport = async () => {
            try {
                const data = await getSessionReport(sessionId);
                setReport(data);
            } catch (err) {
                console.error("Failed to load report", err);
            } finally {
                setLoading(false);
            }
        };
        loadReport();
    }, [sessionId]);

    if (loading) {
        return (
            <div className="flex flex-col items-center justify-center h-[60vh]">
                <Loader2 className="w-12 h-12 text-blue-500 animate-spin mb-4" />
                <p className="text-gray-400">Calculating your score...</p>
            </div>
        );
    }

    if (!report) {
        return <div className="text-center text-red-400">Failed to load report.</div>;
    }

    return (
        <div className="max-w-4xl mx-auto p-8">
            <div className="text-center mb-12">
                <h2 className="text-3xl font-bold text-white mb-2">Gauntlet Complete</h2>
                <p className="text-gray-400">Here is how you performed under pressure.</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-12">
                {/* Overall Score */}
                <div className="bg-gray-800 rounded-xl p-8 flex flex-col items-center justify-center border border-gray-700 col-span-1 md:col-span-3 lg:col-span-1">
                    <div className="relative w-40 h-40 flex items-center justify-center mb-4">
                        <svg className="w-full h-full transform -rotate-90">
                            <circle
                                cx="80"
                                cy="80"
                                r="70"
                                stroke="currentColor"
                                strokeWidth="10"
                                fill="transparent"
                                className="text-gray-700"
                            />
                            <circle
                                cx="80"
                                cy="80"
                                r="70"
                                stroke="currentColor"
                                strokeWidth="10"
                                fill="transparent"
                                strokeDasharray={440}
                                strokeDashoffset={440 - (440 * report.overall_score) / 100}
                                className={clsx(
                                    report.overall_score >= 80 ? "text-green-500" :
                                        report.overall_score >= 60 ? "text-yellow-500" : "text-red-500"
                                )}
                            />
                        </svg>
                        <div className="absolute inset-0 flex flex-col items-center justify-center">
                            <span className="text-4xl font-bold text-white">{report.overall_score}</span>
                            <span className="text-sm text-gray-400">Overall</span>
                        </div>
                    </div>
                </div>

                {/* Strengths */}
                <div className="bg-gray-800 rounded-xl p-6 border border-gray-700">
                    <h3 className="flex items-center text-lg font-bold text-green-400 mb-4">
                        <CheckCircle className="w-5 h-5 mr-2" /> Strengths
                    </h3>
                    <ul className="space-y-2">
                        {report.strengths.length > 0 ? (
                            report.strengths.map((s, i) => (
                                <li key={i} className="text-gray-300 text-sm">• {s}</li>
                            ))
                        ) : (
                            <li className="text-gray-500 text-sm italic">No specific strengths detected.</li>
                        )}
                    </ul>
                </div>

                {/* Weaknesses */}
                <div className="bg-gray-800 rounded-xl p-6 border border-gray-700">
                    <h3 className="flex items-center text-lg font-bold text-red-400 mb-4">
                        <AlertTriangle className="w-5 h-5 mr-2" /> Areas for Improvement
                    </h3>
                    <ul className="space-y-2">
                        {report.weaknesses.length > 0 ? (
                            report.weaknesses.map((w, i) => (
                                <li key={i} className="text-gray-300 text-sm">• {w}</li>
                            ))
                        ) : (
                            <li className="text-gray-500 text-sm italic">No major weaknesses detected.</li>
                        )}
                    </ul>
                </div>
            </div>

            {/* Persona Breakdown */}
            <h3 className="text-xl font-bold text-white mb-6">Persona Breakdown</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-12">
                {report.persona_breakdown.map((p) => (
                    <div key={p.persona_id} className="bg-gray-800 p-4 rounded-lg border border-gray-700">
                        <div className="flex justify-between items-center mb-2">
                            <span className="font-medium text-gray-300 capitalize">{p.persona_id}</span>
                            <span className={clsx(
                                "font-bold",
                                p.average_score >= 80 ? "text-green-400" :
                                    p.average_score >= 60 ? "text-yellow-400" : "text-red-400"
                            )}>{p.average_score}%</span>
                        </div>
                        <div className="w-full bg-gray-700 rounded-full h-2">
                            <div
                                className={clsx(
                                    "h-2 rounded-full",
                                    p.average_score >= 80 ? "bg-green-500" :
                                        p.average_score >= 60 ? "bg-yellow-500" : "bg-red-500"
                                )}
                                style={{ width: `${p.average_score}%` }}
                            />
                        </div>
                        <p className="text-xs text-gray-500 mt-2">{p.total_challenges} challenges</p>
                    </div>
                ))}
            </div>

            <div className="flex justify-center">
                <button
                    onClick={onRestart}
                    className="flex items-center px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-colors"
                >
                    <RefreshCw className="w-5 h-5 mr-2" />
                    Run Another Gauntlet
                </button>
            </div>
        </div>
    );
};
