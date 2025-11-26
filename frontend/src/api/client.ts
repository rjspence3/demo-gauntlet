import axios from 'axios';

const api = axios.create({
    baseURL: '/', // Proxy handles the rest
    headers: {
        'Content-Type': 'application/json',
    },
});

export interface UploadResponse {
    session_id: string;
    filename: string;
    slide_count: number;
    status: string;
}

export interface ResearchDossier {
    session_id: string;
    competitor_insights: string[];
    cost_benchmarks: string[];
    compliance_notes: string[];
    implementation_risks: string[];
    sources: string[];
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
    context_source: string;
    difficulty: string;
    slide_index?: number;
    ideal_answer: string;
}

export interface PersonaScore {
    persona_id: string;
    average_score: number;
    total_challenges: number;
}

export interface SessionReport {
    overall_score: number;
    persona_breakdown: PersonaScore[];
    total_challenges: number;
    strengths: string[];
    weaknesses: string[];
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
