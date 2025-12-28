/**
 * API Client for Noesis Backend
 * Handles all HTTP requests to the FastAPI backend
 */
import axios from 'axios';
import type { Block, BlockVersion, Document } from '../stores/noesis-store';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// ============================================================================
// Document API
// ============================================================================

export const documentApi = {
    /**
     * Create a new document
     */
    create: async (data: {
        title: string;
        tags?: string[];
        folder_path?: string;
    }): Promise<Document> => {
        const response = await api.post('/documents', data);
        return response.data;
    },

    /**
     * List documents in a folder
     */
    list: async (folderPath: string = '/'): Promise<Document[]> => {
        const response = await api.get('/documents', {
            params: { folder_path: folderPath },
        });
        return response.data;
    },

    /**
     * Get a document with all its blocks
     */
    get: async (documentId: string): Promise<Document> => {
        const response = await api.get(`/documents/${documentId}`);
        return response.data;
    },

    /**
     * Update document metadata
     */
    update: async (
        documentId: string,
        updates: {
            title?: string;
            tags?: string[];
            folder_path?: string;
        }
    ): Promise<Document> => {
        const response = await api.patch(`/documents/${documentId}`, updates);
        return response.data;
    },

    /**
     * Delete a document
     */
    delete: async (documentId: string): Promise<void> => {
        await api.delete(`/documents/${documentId}`);
    },
};

// ============================================================================
// Block API
// ============================================================================

export const blockApi = {
    /**
     * Create a new block
     */
    create: async (data: {
        document_id: string;
        position_index: number;
        block_type?: 'paragraph' | 'header' | 'quote' | 'axiom' | 'list';
        initial_content: string;
    }): Promise<Block> => {
        const response = await api.post('/blocks', data);
        return response.data;
    },

    /**
     * Get a block with its active version
     */
    get: async (blockId: string): Promise<Block> => {
        const response = await api.get(`/blocks/${blockId}`);
        return response.data;
    },

    /**
     * Get all versions of a block (the version stack)
     */
    getVersions: async (blockId: string): Promise<BlockVersion[]> => {
        const response = await api.get(`/blocks/${blockId}/versions`);
        return response.data;
    },

    /**
     * Create a new version (push to stack)
     */
    createVersion: async (
        blockId: string,
        data: {
            content: string;
            author_type?: string;
            transform_intent?: string;
            transform_params?: Record<string, any>;
        }
    ): Promise<BlockVersion> => {
        const response = await api.post(`/blocks/${blockId}/versions`, data);
        return response.data;
    },

    /**
     * Activate a specific version
     */
    activateVersion: async (
        blockId: string,
        versionId: string
    ): Promise<BlockVersion> => {
        const response = await api.patch(
            `/blocks/${blockId}/versions/${versionId}/activate`
        );
        return response.data;
    },

    /**
     * Update block metadata
     */
    update: async (
        blockId: string,
        updates: {
            position_index?: number;
            block_type?: 'paragraph' | 'header' | 'quote' | 'axiom' | 'list';
        }
    ): Promise<Block> => {
        const response = await api.patch(`/blocks/${blockId}`, updates);
        return response.data;
    },

    /**
     * Delete a block
     */
    delete: async (blockId: string): Promise<void> => {
        await api.delete(`/blocks/${blockId}`);
    },
};

// ============================================================================
// AI API - The Magic!
// ============================================================================

export interface TransformRequest {
    block_id: string;
    thinker: string;
    intent: 'critique' | 'steelman' | 'simplify' | 'mystify' | 'expand' | 'condense';
    style?: string;
    model?: string;
    output_length?: 'brief' | 'short' | 'medium' | 'detailed' | 'extensive';
    custom_persona?: string;
}

export interface TransformResponse {
    original_version_id: string;
    new_version_id: string;
    original_content: string;
    transformed_content: string;
    thinker: string;
    intent: string;
}

export interface LogicAnalysisResponse {
    fallacies: Array<{
        type: string;
        location: string;
        explanation: string;
    }>;
    assumptions: Array<{
        assumption: string;
        explanation: string;
    }>;
    undefined_terms: string[];
    structure: {
        premises: string[];
        conclusion: string;
    };
    raw_analysis?: string;
}

export const aiApi = {
    /**
     * Transform a block through a philosophical lens (Thinker Mode)
     */
    transform: async (request: TransformRequest): Promise<TransformResponse> => {
        const response = await api.post('/ai/transform', request);
        return response.data;
    },

    /**
     * Transform with streaming (Server-Sent Events)
     * Returns an EventSource for real-time updates
     */
    transformStream: (request: TransformRequest): EventSource => {
        const params = new URLSearchParams({
            block_id: request.block_id,
            thinker: request.thinker,
            intent: request.intent,
            ...(request.style && { style: request.style }),
            ...(request.model && { model: request.model }),
        });

        const url = `${API_BASE_URL}/ai/transform/stream?${params}`;
        return new EventSource(url);
    },

    /**
     * Analyze the logical structure of text (The Oracle)
     */
    analyze: async (content: string): Promise<LogicAnalysisResponse> => {
        const response = await api.post('/ai/analyze', { content });
        return response.data;
    },

    /**
     * Get list of available thinkers and intents
     */
    getThinkers: async (): Promise<{
        thinkers: Array<{
            id: string;
            name: string;
            description: string;
            style_suggestions: string[];
        }>;
        intents: Array<{
            id: string;
            description: string;
        }>;
    }> => {
        const response = await api.get('/ai/thinkers');
        return response.data;
    },
};

// ============================================================================
// Error Handling
// ============================================================================

api.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response) {
            // Server responded with error
            console.error('API Error:', error.response.data);
            throw new Error(error.response.data.detail || 'An error occurred');
        } else if (error.request) {
            // Request made but no response
            console.error('Network Error:', error.request);
            throw new Error('Network error - please check your connection');
        } else {
            // Something else happened
            console.error('Error:', error.message);
            throw error;
        }
    }
);

export default api;
