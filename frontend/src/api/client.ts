import axios from 'axios';

const api = axios.create({
    baseURL: import.meta.env.VITE_API_URL || '/', // Use env var or fall back to proxy
    headers: {
        'Content-Type': 'application/json',
    },
});

// Add auth token to requests if available
export const setAuthToken = (token: string | null) => {
    if (token) {
        api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    } else {
        delete api.defaults.headers.common['Authorization'];
    }
};

// Handle 401 responses
api.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response?.status === 401) {
            // Clear token and redirect to login if needed
            // For now, we'll just let the caller handle the error or App.tsx handle the state
            setAuthToken(null);
            localStorage.removeItem('token');
            window.location.href = '/'; // Simple redirect to root/login
        }
        return Promise.reject(error);
    }
);

export interface Token {
    access_token: string;
    token_type: string;
}

export const loginWithCode = async (inviteCode: string): Promise<Token> => {
    const response = await api.post<Token>('/auth/login-with-code', {
        invite_code: inviteCode
    });
    return response.data;
};

export interface UploadResponse {
    session_id: string;
    filename: string;
    slide_count: number;
    status: string;
}

export interface Fact {
    id: string;
    topic: string;
    text: string;
    source_url: string;
    source_title: string;
    domain: string;
    snippet: string;
}

export interface ResearchDossier {
    session_id: string;
    competitor_insights: string[];
    cost_benchmarks: string[];
    compliance_notes: string[];
    implementation_risks: string[];
    sources: string[];
    facts?: Fact[];
}

export interface ChallengerPersona {
    id: string;
    name: string;
    role: string;
    style: string;
    focus_areas: string[];
}

export interface Slide {
    index: number;
    title: string;
    text: string;
    notes: string;
    tags: string[];
}

export interface Challenge {
    id: string;
    session_id: string;
    persona_id: string;
    question: string;
    difficulty: string;
    slide_index?: number;
    ideal_answer: string;
    evidence?: {
        chunks: string[];
        facts: Fact[];
    };
}

export interface ScoreResponse {
    score: number;
    feedback: string;
}

export interface PersonaScore {
    persona_id: string;
    average_score: number;
    total_challenges: number;
    component_scores?: Record<string, number>;
}

export interface SessionReport {
    overall_score: number;
    persona_breakdown: PersonaScore[];
    total_challenges: number;
    strengths: string[];
    weaknesses: string[];
    slide_breakdown: Record<number, number>;
}

export const uploadDeck = async (file: File): Promise<UploadResponse> => {
    const formData = new FormData();
    formData.append('file', file);
    const response = await api.post<UploadResponse>('/ingestion/upload', formData, {
        headers: {
            'Content-Type': 'multipart/form-data',
        },
    });
    return response.data;
};

export const generateResearch = async (sessionId: string): Promise<ResearchDossier> => {
    const response = await api.post<ResearchDossier>(`/research/generate/${sessionId}`);
    return response.data;
};

export const listPersonas = async (): Promise<ChallengerPersona[]> => {
    const response = await api.get<ChallengerPersona[]>('/challenges/personas');
    return response.data;
};

export const getSlides = async (sessionId: string): Promise<Slide[]> => {
    const response = await api.get<Slide[]>(`/ingestion/session/${sessionId}/slides`);
    return response.data;
};

export const getSessionStatus = async (sessionId: string): Promise<{ status: string }> => {
    const response = await api.get<{ status: string }>(`/ingestion/session/${sessionId}/status`);
    return response.data;
};

export const submitAnswer = async (
    sessionId: string,
    personaId: string,
    challengeId: string,
    userAnswer: string,
    idealAnswer: string
): Promise<ScoreResponse> => {
    const response = await api.post<ScoreResponse>('/evaluation/score', {
        session_id: sessionId,
        persona_id: personaId,
        challenge_id: challengeId,
        user_answer: userAnswer,
        ideal_answer: idealAnswer
    });
    return response.data;
};

export const generateChallenges = async (
    sessionId: string,
    personaId: string,
    slideIndex?: number,
    slideContent?: string
): Promise<Challenge[]> => {
    const response = await api.post<Challenge[]>('/challenges/generate', {
        session_id: sessionId,
        persona_id: personaId,
        slide_index: slideIndex,
        slide_content: slideContent
    });
    return response.data;
};

export const getChallenges = async (sessionId: string): Promise<Challenge[]> => {
    const response = await api.get<Challenge[]>(`/challenges/session/${sessionId}`);
    return response.data;
};

export const getSessionReport = async (sessionId: string): Promise<SessionReport> => {
    const response = await api.get<SessionReport>(`/evaluation/report/${sessionId}`);
    return response.data;
};

export const precomputeChallenges = async (sessionId: string, personaIds: string[]): Promise<void> => {
    await api.post(`/research/precompute/${sessionId}`, {
        persona_ids: personaIds
    });
};
