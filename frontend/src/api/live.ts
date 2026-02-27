export type AgentState = {
    persona_id: string;
    status: 'listening' | 'thinking' | 'raising_hand' | 'speaking';
    message?: string;
};

export type SessionState = {
    transcript_length: number;
    agents: AgentState[];
};

export type LiveEvent =
    | { type: 'state_update'; data: SessionState }
    | { type: 'error'; message: string };

type Listener = (event: LiveEvent) => void;

class LiveClient {
    private ws: WebSocket | null = null;
    private listeners: Listener[] = [];
    private url: string;
    private messageQueue: string[] = [];
    private reconnectAttempts = 0;
    private maxReconnectAttempts = 5;

    constructor() {
        const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const apiUrl = import.meta.env.VITE_API_URL as string | undefined;
        if (apiUrl) {
            // Derive WebSocket URL from the API base URL (same host, same proxy)
            this.url = apiUrl.replace(/^https?:/, wsProtocol) + '/live/ws';
        } else {
            // Same host, let Vite/Caddy proxy handle it
            this.url = `${wsProtocol}//${window.location.host}/live/ws`;
        }
    }

    connect() {
        if (this.ws && (this.ws.readyState === WebSocket.OPEN || this.ws.readyState === WebSocket.CONNECTING)) {
            return;
        }

        this.ws = new WebSocket(this.url);

        this.ws.onopen = () => {
            console.log('Connected to Live Session');
            this.reconnectAttempts = 0;
            this.processQueue();
        };

        this.ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                this.notify(data);
            } catch (e) {
                console.error('Failed to parse WS message', e);
            }
        };

        this.ws.onclose = () => {
            console.log('Disconnected from Live Session');
            this.ws = null;
            if (this.reconnectAttempts < this.maxReconnectAttempts) {
                setTimeout(() => {
                    this.reconnectAttempts++;
                    this.connect();
                }, 1000 * this.reconnectAttempts);
            }
        };

        this.ws.onerror = (error) => {
            console.error('WS Error:', error);
            this.notify({ type: 'error', message: 'Connection error' });
        };
    }

    private processQueue() {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            while (this.messageQueue.length > 0) {
                const msg = this.messageQueue.shift();
                if (msg) this.ws.send(msg);
            }
        }
    }

    private send(data: any) {
        const msg = JSON.stringify(data);
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(msg);
        } else {
            this.messageQueue.push(msg);
            if (!this.ws || this.ws.readyState === WebSocket.CLOSED) {
                this.connect();
            }
        }
    }

    subscribe(callback: Listener) {
        this.listeners.push(callback);
        return () => {
            this.listeners = this.listeners.filter(l => l !== callback);
        };
    }

    private notify(event: LiveEvent) {
        this.listeners.forEach(l => l(event));
    }

    sendTranscriptChunk(text: string) {
        this.send({
            type: 'transcript_chunk',
            text
        });
    }

    initSession(sessionId: string, personaIds: string[]) {
        this.send({
            type: 'init_session',
            session_id: sessionId,
            persona_ids: personaIds
        });
    }

    disconnect() {
        if (this.ws) {
            this.ws.onclose = null; // Prevent reconnect
            this.ws.close();
            this.ws = null;
            this.messageQueue = [];
        }
    }
}

export const liveClient = new LiveClient();
