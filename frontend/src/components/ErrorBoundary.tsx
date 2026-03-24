import React from 'react';
import { AlertTriangle, RefreshCw } from 'lucide-react';

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
        localStorage.removeItem('dg_session_id');
        this.setState({ hasError: false, error: null });
        window.location.href = '/';
    };

    render() {
        if (this.state.hasError) {
            return (
                <div className="min-h-screen bg-page flex items-center justify-center p-6">
                    <div className="max-w-sm w-full text-center">
                        <div className="w-14 h-14 bg-brand-50 rounded-2xl flex items-center justify-center mx-auto mb-6">
                            <AlertTriangle className="w-7 h-7 text-brand-500" />
                        </div>
                        <h1 className="text-xl font-bold text-text-primary mb-2 tracking-tight">Something went wrong</h1>
                        <p className="text-text-muted text-sm mb-8 leading-relaxed">
                            An unexpected error occurred. Start a new session to continue.
                        </p>
                        <button
                            onClick={this.handleReset}
                            className="inline-flex items-center gap-2 bg-brand-500 text-white font-semibold text-sm px-6 py-3 rounded-xl hover:bg-brand-600 transition-all shadow-sm hover:shadow-md"
                        >
                            <RefreshCw className="w-4 h-4" />
                            Start Over
                        </button>
                    </div>
                </div>
            );
        }

        return this.props.children;
    }
}
