import React from 'react';
import { Swords, RefreshCw } from 'lucide-react';

interface ErrorBoundaryState {
    hasError: boolean;
    error: Error | null;
}

interface ErrorBoundaryProps {
    children: React.ReactNode;
}

export class ErrorBoundary extends React.Component<ErrorBoundaryProps, ErrorBoundaryState> {
    constructor(props: ErrorBoundaryProps) {
        super(props);
        this.state = { hasError: false, error: null };
    }

    static getDerivedStateFromError(error: Error): ErrorBoundaryState {
        return { hasError: true, error };
    }

    componentDidCatch(error: Error, info: React.ErrorInfo) {
        console.error('ErrorBoundary caught:', error, info);
    }

    handleReset = () => {
        this.setState({ hasError: false, error: null });
        window.location.href = '/';
    };

    render() {
        if (this.state.hasError) {
            return (
                <div className="min-h-screen bg-zinc-50 flex items-center justify-center p-6">
                    <div className="max-w-md w-full text-center">
                        <div className="w-16 h-16 bg-orange-50 rounded-2xl flex items-center justify-center mx-auto mb-6">
                            <Swords className="w-8 h-8 text-orange-500" />
                        </div>
                        <h1 className="text-2xl font-bold text-slate-900 mb-2">Something went wrong</h1>
                        <p className="text-slate-500 mb-2">
                            Demo Gauntlet hit an unexpected error. Your session data may still be intact.
                        </p>
                        {this.state.error && (
                            <p className="text-xs text-slate-400 font-mono bg-slate-100 rounded-lg p-3 mb-6 text-left break-all">
                                {this.state.error.message}
                            </p>
                        )}
                        <button
                            onClick={this.handleReset}
                            className="inline-flex items-center gap-2 bg-orange-500 text-white font-bold px-6 py-2.5 rounded-full hover:bg-orange-600 transition-colors"
                        >
                            <RefreshCw className="w-4 h-4" />
                            Restart App
                        </button>
                    </div>
                </div>
            );
        }

        return this.props.children;
    }
}
