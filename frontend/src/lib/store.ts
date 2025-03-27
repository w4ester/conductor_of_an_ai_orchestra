import { writable } from 'svelte/store';
import type { User } from './api';

// Interface for auth state
interface AuthState {
  isAuthenticated: boolean;
  user: User | null;
  loading: boolean;
  error: string | null;
}

// Default auth state
const defaultAuthState: AuthState = {
  isAuthenticated: false,
  user: null,
  loading: false,
  error: null
};

// Create writable store with default values
export const authStore = writable<AuthState>(defaultAuthState);

// Models store
export const modelsStore = writable<any[]>([]);

// Prompts store
export const promptsStore = writable<any[]>([]);

// Tools store
export const toolsStore = writable<any[]>([]);

// Documents store
export const documentsStore = writable<any[]>([]);

// RAG systems store
export const ragSystemsStore = writable<any[]>([]);

// Vector databases store
export const vectorDbsStore = writable<any[]>([]);

// Embeddings store
export const embeddingsStore = writable<any[]>([]);

// Embedding models store
export const embeddingModelsStore = writable<any[]>([]);

// Vector DB types store
export const vectorDbTypesStore = writable<any[]>([]);