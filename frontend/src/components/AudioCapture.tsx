import React, { useState, useEffect, useCallback } from 'react';
import { Mic, MicOff, AlertCircle } from 'lucide-react';
import { liveClient } from '../api/live';

interface AudioCaptureProps {
    onTranscript: (text: string) => void;
}

declare global {
    interface Window {
        SpeechRecognition: unknown;
        webkitSpeechRecognition: unknown;
    }
}

export const AudioCapture: React.FC<AudioCaptureProps> = ({ onTranscript }) => {
    const [isListening, setIsListening] = useState(false);
    const [error, setError] = useState<string | null>(null);
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const [recognition, setRecognition] = useState<any>(null);

    useEffect(() => {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (!SpeechRecognition) {
            setError('Browser does not support Speech Recognition.');
            return;
        }

        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        const recognitionInstance = new (SpeechRecognition as any)();
        recognitionInstance.continuous = true;
        recognitionInstance.interimResults = true;
        recognitionInstance.lang = 'en-US';

        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        recognitionInstance.onresult = (event: any) => {
            let finalTranscript = '';
            for (let i = event.resultIndex; i < event.results.length; ++i) {
                if (event.results[i].isFinal) {
                    finalTranscript += event.results[i][0].transcript;
                }
            }
            if (finalTranscript) {
                onTranscript(finalTranscript);
                liveClient.sendTranscriptChunk(finalTranscript);
            }
        };

        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        recognitionInstance.onerror = (event: any) => {
            console.error('Speech recognition error', event.error);
            if (event.error === 'not-allowed') {
                setError('Microphone permission denied.');
                setIsListening(false);
            }
        };

        recognitionInstance.onend = () => {
            if (isListening) {
                setIsListening(false);
            }
        };

        setRecognition(recognitionInstance);
    }, [onTranscript]);

    const toggleListening = useCallback(() => {
        if (!recognition) return;

        if (isListening) {
            recognition.stop();
            setIsListening(false);
        } else {
            setError(null);
            try {
                recognition.start();
                setIsListening(true);
            } catch (e) {
                console.error("Failed to start recognition", e);
            }
        }
    }, [recognition, isListening]);

    return (
        <div className="flex flex-col items-center gap-3 p-5 border border-border-ai rounded-2xl bg-white/80 backdrop-blur-sm">
            <div className="flex items-center gap-4">
                <button
                    onClick={toggleListening}
                    className={[
                        'p-4 rounded-2xl transition-all',
                        isListening
                            ? 'bg-status-error/10 text-status-error hover:bg-status-error/20 animate-soft-pulse'
                            : 'bg-ai-50 text-ai-500 hover:bg-ai-100'
                    ].join(' ')}
                >
                    {isListening ? <Mic className="w-6 h-6" /> : <MicOff className="w-6 h-6" />}
                </button>

                <div className="flex flex-col">
                    <span className="font-semibold text-sm text-text-primary">
                        {isListening ? 'Listening...' : 'Microphone Off'}
                    </span>
                    <span className="text-xs text-text-faint">
                        {isListening ? 'Speak clearly into your mic' : 'Click to start presentation'}
                    </span>
                </div>
            </div>

            {error && (
                <div className="flex items-center gap-2 text-status-error text-sm">
                    <AlertCircle className="w-4 h-4" />
                    <span>{error}</span>
                </div>
            )}
        </div>
    );
};
