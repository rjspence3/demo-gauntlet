import React, { useState } from 'react';
import { loginWithCode, setAuthToken } from '../api/client';
import { Lock, ArrowRight, ShieldCheck } from 'lucide-react';
import { DGCard, DGInput, DGButton } from './ui';

interface AuthViewProps {
    onAuthSuccess: () => void;
}

export function AuthView({ onAuthSuccess }: AuthViewProps) {
    const [inviteCode, setInviteCode] = useState('');
    const [error, setError] = useState<string | null>(null);
    const [isLoading, setIsLoading] = useState(false);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError(null);
        setIsLoading(true);

        try {
            const tokenData = await loginWithCode(inviteCode);
            setAuthToken(tokenData.access_token);
            localStorage.setItem('token', tokenData.access_token);
            onAuthSuccess();
        } catch (err: any) {
            console.error('Auth error:', err);
            if (err.response?.status === 401) {
                setError('Invalid invite code');
            } else if (err.response?.data?.detail) {
                setError(err.response.data.detail);
            } else {
                setError('Authentication failed. Please try again.');
            }
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center bg-[#050505] relative overflow-hidden px-4">
            {/* Background Effects */}
            <div className="absolute inset-0 pointer-events-none">
                <div className="absolute top-0 left-1/4 w-64 sm:w-96 h-64 sm:h-96 bg-cyan-400/10 rounded-full blur-3xl animate-pulse"></div>
                <div className="absolute bottom-0 right-1/4 w-64 sm:w-96 h-64 sm:h-96 bg-violet-500/10 rounded-full blur-3xl animate-pulse delay-1000"></div>
            </div>

            <div className="w-full max-w-md p-4 sm:p-8 relative z-10">
                <div className="text-center mb-6 sm:mb-8">
                    <div className="inline-flex items-center justify-center w-14 sm:w-16 h-14 sm:h-16 rounded-xl bg-gradient-to-br from-cyan-400/20 to-violet-500/20 border border-slate-700 mb-4 shadow-[0_0_15px_rgba(34,211,238,0.3)]">
                        <Lock className="w-7 sm:w-8 h-7 sm:h-8 text-white" />
                    </div>
                    <h1 className="text-2xl sm:text-3xl font-bold text-white mb-2 tracking-tight">
                        Beta Access
                    </h1>
                    <p className="text-slate-400 text-sm sm:text-base">
                        Enter your invite code to access the Gauntlet.
                    </p>
                </div>

                <DGCard variant="elevated" className="p-6 sm:p-8">
                    <form onSubmit={handleSubmit} className="space-y-4">
                        {error && (
                            <div className="p-3 rounded-xl bg-rose-500/20 border border-rose-500/50 text-rose-200 text-sm text-center">
                                {error}
                            </div>
                        )}

                        <DGInput
                            label="Invite Code"
                            type="text"
                            value={inviteCode}
                            onChange={(e) => setInviteCode(e.target.value)}
                            placeholder="BETA-XXXX-XXXX"
                            icon={<ShieldCheck className="w-5 h-5" />}
                            required
                        />

                        <DGButton
                            type="submit"
                            variant="primary"
                            size="lg"
                            loading={isLoading}
                            className="w-full mt-6"
                        >
                            Access System
                            <ArrowRight className="w-4 h-4 ml-2" />
                        </DGButton>
                    </form>
                </DGCard>
            </div>
        </div>
    );
}
