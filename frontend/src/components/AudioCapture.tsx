import React, { useState, useEffect, useCallback } from 'react';
import { Mic, MicOff, AlertCircle } from 'lucide-react';
import { Button } from './ui/button'; // Assuming Shadcn or similar, or fallback to native
import { liveClient } from '../api/live';

interface AudioCaptureProps {
    onTranscript: (text: string) => void;
}

// Extend window interface for Web Speech API
declare global {
    interface Window {
        SpeechRecognition: any;
        webkitSpeechRecognition: any;
    }
}

export const AudioCapture: React.FC<AudioCaptureProps> = ({ onTranscript }) => {
    const [isListening, setIsListening] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [recognition, setRecognition] = useState<any>(null);

    useEffect(() => {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (!SpeechRecognition) {
            setError('Browser does not support Speech Recognition.');
            return;
        }

        const recognitionInstance = new SpeechRecognition();
        recognitionInstance.continuous = true;
        recognitionInstance.interimResults = true;
        recognitionInstance.lang = 'en-US';

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

        recognitionInstance.onerror = (event: any) => {
            console.error('Speech recognition error', event.error);
            if (event.error === 'not-allowed') {
                setError('Microphone permission denied.');
                setIsListening(false);
            }
        };

        recognitionInstance.onend = () => {
            // If we were supposed to be listening, restart (continuous loop)
            // But we manage state via react, so we might need to be careful not to create infinite loop if error
            if (isListening) {
                // recognitionInstance.start(); 
                // Note: some browsers stop automatically. For this demo, we might let it stop.
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
        <div className="flex flex-col items-center gap-2 p-4 border border-slate-700 rounded-lg bg-slate-900/50">
            <div className="flex items-center gap-4">
                <button
                    onClick={toggleListening}
                    className={`p-4 rounded-full transition-all ${isListening
                            ? 'bg-red-500/20 text-red-500 hover:bg-red-500/30 animate-pulse'
                            : 'bg-cyan-500/20 text-cyan-400 hover:bg-cyan-500/30'
                        }`}
                >
                    {isListening ? <Mic className="w-6 h-6" /> : <MicOff className="w-6 h-6" />}
                </button>

                <div className="flex flex-col">
                    <span className="font-semibold text-slate-200">
                        {isListening ? 'Listening...' : 'Microphone Off'}
                    </span>
                    <span className="text-xs text-slate-500">
                        {isListening ? 'Speak clearly into your mic' : 'Click to start presentation'}
                    </span>
                </div>
            </div>

            {error && (
                <div className="flex items-center gap-2 text-red-400 text-sm mt-2">
                    <AlertCircle className="w-4 h-4" />
                    <span>{error}</span>
                </div>
            )}
        </div>
    );
};
