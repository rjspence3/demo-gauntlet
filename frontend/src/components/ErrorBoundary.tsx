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
                <div className="min-h-screen bg-gray-50 flex items-center justify-center p-6">
                    <div className="max-w-sm w-full text-center">
                        <div className="w-12 h-12 bg-status-error/10 rounded-xl flex items-center justify-center mx-auto mb-5">
                            <AlertTriangle className="w-6 h-6 text-status-error" />
                        </div>
                        <h1 className="text-lg font-semibold text-text-primary mb-2">Something went wrong</h1>
                        <p className="text-text-muted text-sm mb-6">
                            An unexpected error occurred. Start a new session to continue.
                        </p>
                        <button
                            onClick={this.handleReset}
                            className="inline-flex items-center gap-2 bg-brand-500 text-white font-medium text-sm px-5 py-2.5 rounded-lg hover:bg-brand-400 transition-colors"
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
