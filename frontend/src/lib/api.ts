// API client for interacting with backend
// Uses fetch API to make HTTP requests

// Backend URL - replace with environment variable in production
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Interface for login request
interface LoginCredentials {
  username: string;
  password: string;
}

// Interface for user data
export interface User {
  email: string;
  username: string;
  full_name?: string;
  disabled?: boolean;
  is_admin?: boolean;
}

// Interface for auth token
export interface AuthToken {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

// Interface for Ollama models
export interface OllamaModel {
  name: string;
  id: string;
  size: string;
  modified: string;
}

// Interface for Prompt
export interface Prompt {
  id?: string;
  title: string;
  content: string;
  model: string;
  category?: string;
  tags?: string[];
  creator_id?: string;
  created_at?: string;
  updated_at?: string;
}

// Response interfaces with pagination
export interface PromptResponse {
  items: Prompt[];
  total: number;
}

// Interface for Tool
export interface Tool {
  id?: string;
  name: string;
  description: string;
  code: string;
  language: string;
  creator_id?: string;
  created_at?: string;
  updated_at?: string;
}

// Response interfaces with pagination
export interface ToolResponse {
  items: Tool[];
  total: number;
}

// Interface for Document
export interface Document {
  id?: string;
  title: string;
  content: string;
  file_type: string;
  creator_id?: string;
  created_at?: string;
}

// Response interfaces with pagination
export interface DocumentResponse {
  items: Document[];
  total: number;
}

// Interface for RAG System
export interface RAGSystem {
  id?: string;
  name: string;
  description: string;
  embedding_model: string;
  documents: string[];
  creator_id?: string;
  created_at?: string;
  updated_at?: string;
}

// Response interfaces with pagination
export interface RAGSystemResponse {
  items: RAGSystem[];
  total: number;
}

// Interface for Vector Database
export interface VectorDatabase {
  id?: string;
  name: string;
  type: string;
  connection_string?: string;
  creator_id?: string;
  created_at?: string;
  updated_at?: string;
}

// Response interfaces with pagination
export interface VectorDatabaseResponse {
  items: VectorDatabase[];
  total: number;
}

// Interface for VectorDB Type
export interface VectorDBType {
  name: string;
  description: string;
}

// Interface for Embedding
export interface Embedding {
  id?: string;
  document_id: string;
  vector_db_id: string;
  model: string;
  dimensions: number;
  status: string;
  error?: string;
  creator_id?: string;
  created_at?: string;
  completed_at?: string;
  chunks?: any[];
}

// Response interfaces with pagination
export interface EmbeddingResponse {
  items: Embedding[];
  total: number;
}

// Interface for Embedding Model
export interface EmbeddingModel {
  name: string;
  dimensions: number;
  description: string;
}

// Interface for Embedding Request
export interface EmbeddingRequest {
  document_id: string;
  vector_db_id: string;
  model: string;
  chunk_size?: number;
  chunk_overlap?: number;
}

// Interface for Embedding Task Response
export interface EmbeddingTaskResponse {
  task_id: string;
  embedding_id: string;
  status: string;
}

// Interface for Task Status
export interface TaskStatus {
  task_id: string;
  status: string;
  result?: any;
  error?: string;
  created_at?: number;
  started_at?: number;
  completed_at?: number;
  duration?: number;
}

// API client class
class ApiClient {
  private token: string | null = null;

  constructor() {
    // Check if we have a token in localStorage
    this.token = localStorage.getItem('auth_token');
  }

  // Set authentication token
  setToken(token: string) {
    this.token = token;
    localStorage.setItem('auth_token', token);
  }

  // Clear authentication token
  clearToken() {
    this.token = null;
    localStorage.removeItem('auth_token');
  }

  // Get authentication headers
  private getHeaders() {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    };

    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }

    return headers;
  }

  // Handle API errors
  private async handleResponse<T>(response: Response): Promise<T> {
    if (!response.ok) {
      // Try to get error details from response
      try {
        const errorData = await response.json();
        throw new Error(errorData.detail || `API error: ${response.status}`);
      } catch (e) {
        throw new Error(`API error: ${response.status}`);
      }
    }
    return response.json();
  }

  // Login and get token
  async login(credentials: LoginCredentials): Promise<User> {
    // Convert credentials to form data format required by OAuth2
    const formData = new URLSearchParams();
    formData.append('username', credentials.username);
    formData.append('password', credentials.password);

    const response = await fetch(`${API_URL}/api/v1/auth/token`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      },
      body: formData
    });

    const data = await this.handleResponse<AuthToken>(response);
    this.setToken(data.access_token);
    
    // Get and return user info
    return await this.getCurrentUser();
  }

  // Refresh token
  async refreshToken(refreshToken: string): Promise<AuthToken> {
    const response = await fetch(`${API_URL}/api/v1/auth/refresh`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ refresh_token: refreshToken })
    });

    const data = await this.handleResponse<AuthToken>(response);
    this.setToken(data.access_token);
    return data;
  }

  // Get current user
  async getCurrentUser(): Promise<User> {
    const response = await fetch(`${API_URL}/api/v1/users/me`, {
      headers: this.getHeaders()
    });

    return this.handleResponse<User>(response);
  }

  // Get list of available models
  async getModels(): Promise<OllamaModel[]> {
    const response = await fetch(`${API_URL}/api/v1/models`, {
      headers: this.getHeaders()
    });

    return this.handleResponse<OllamaModel[]>(response);
  }

  // Generate text with a model
  async generate(requestData: any): Promise<any> {
    const response = await fetch(`${API_URL}/api/v1/models/generate`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify(requestData)
    });

    return this.handleResponse<any>(response);
  }
  
  // Create or update a model with a Modelfile
  async createModel(name: string, modelfile: string): Promise<any> {
    const response = await fetch(`${API_URL}/api/v1/models/create`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify({
        name,
        modelfile
      })
    });

    return this.handleResponse<any>(response);
  }
  
  // Get a model's Modelfile
  async getModelfile(name: string): Promise<string> {
    const response = await fetch(`${API_URL}/api/v1/models/${encodeURIComponent(name)}/modelfile`, {
      headers: this.getHeaders()
    });

    const data = await this.handleResponse<{ modelfile: string }>(response);
    return data.modelfile || '';
  }
  
  // Delete a model
  async deleteModel(name: string): Promise<any> {
    const response = await fetch(`${API_URL}/api/v1/models/${encodeURIComponent(name)}`, {
      method: 'DELETE',
      headers: this.getHeaders()
    });

    return this.handleResponse<any>(response);
  }

  // Get embeddings for a text
  async getTextEmbeddings(model: string, text: string): Promise<any> {
    const response = await fetch(`${API_URL}/api/v1/models/embeddings`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify({
        model,
        prompt: text
      })
    });

    return this.handleResponse<any>(response);
  }

  // Check if API is available
  async healthCheck(): Promise<{ status: string }> {
    const response = await fetch(`${API_URL}/api/health`);
    return this.handleResponse<{ status: string }>(response);
  }

  // Detailed health check
  async detailedHealthCheck(): Promise<any> {
    const response = await fetch(`${API_URL}/api/health/detailed`, {
      headers: this.getHeaders()
    });
    return this.handleResponse<any>(response);
  }
  
  // Prompt Management
  
  // Get all prompts
  async getPrompts(page: number = 0, limit: number = 10, category?: string, tag?: string): Promise<PromptResponse> {
    let url = `${API_URL}/api/v1/prompts?skip=${page * limit}&limit=${limit}`;
    if (category) url += `&category=${encodeURIComponent(category)}`;
    if (tag) url += `&tag=${encodeURIComponent(tag)}`;
    
    const response = await fetch(url, {
      headers: this.getHeaders()
    });

    return this.handleResponse<PromptResponse>(response);
  }
  
  // Get a specific prompt
  async getPrompt(id: string): Promise<Prompt> {
    const response = await fetch(`${API_URL}/api/v1/prompts/${id}`, {
      headers: this.getHeaders()
    });

    return this.handleResponse<Prompt>(response);
  }
  
  // Create a new prompt
  async createPrompt(prompt: Prompt): Promise<Prompt> {
    const response = await fetch(`${API_URL}/api/v1/prompts`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify(prompt)
    });

    return this.handleResponse<Prompt>(response);
  }
  
  // Update a prompt
  async updatePrompt(id: string, prompt: Partial<Prompt>): Promise<Prompt> {
    const response = await fetch(`${API_URL}/api/v1/prompts/${id}`, {
      method: 'PUT',
      headers: this.getHeaders(),
      body: JSON.stringify(prompt)
    });

    return this.handleResponse<Prompt>(response);
  }
  
  // Delete a prompt
  async deletePrompt(id: string): Promise<void> {
    const response = await fetch(`${API_URL}/api/v1/prompts/${id}`, {
      method: 'DELETE',
      headers: this.getHeaders()
    });

    if (!response.ok) {
      // Try to get error details from response
      try {
        const errorData = await response.json();
        throw new Error(errorData.detail || `API error: ${response.status}`);
      } catch (e) {
        throw new Error(`API error: ${response.status}`);
      }
    }
  }
  
  // Tool Management
  
  // Get all tools
  async getTools(page: number = 0, limit: number = 10, language?: string): Promise<ToolResponse> {
    let url = `${API_URL}/api/v1/tools?skip=${page * limit}&limit=${limit}`;
    if (language) url += `&language=${encodeURIComponent(language)}`;
    
    const response = await fetch(url, {
      headers: this.getHeaders()
    });

    return this.handleResponse<ToolResponse>(response);
  }
  
  // Get a specific tool
  async getTool(id: string): Promise<Tool> {
    const response = await fetch(`${API_URL}/api/v1/tools/${id}`, {
      headers: this.getHeaders()
    });

    return this.handleResponse<Tool>(response);
  }
  
  // Create a new tool
  async createTool(tool: Tool): Promise<Tool> {
    const response = await fetch(`${API_URL}/api/v1/tools`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify(tool)
    });

    return this.handleResponse<Tool>(response);
  }
  
  // Update a tool
  async updateTool(id: string, tool: Partial<Tool>): Promise<Tool> {
    const response = await fetch(`${API_URL}/api/v1/tools/${id}`, {
      method: 'PUT',
      headers: this.getHeaders(),
      body: JSON.stringify(tool)
    });

    return this.handleResponse<Tool>(response);
  }
  
  // Delete a tool
  async deleteTool(id: string): Promise<void> {
    const response = await fetch(`${API_URL}/api/v1/tools/${id}`, {
      method: 'DELETE',
      headers: this.getHeaders()
    });

    if (!response.ok) {
      try {
        const errorData = await response.json();
        throw new Error(errorData.detail || `API error: ${response.status}`);
      } catch (e) {
        throw new Error(`API error: ${response.status}`);
      }
    }
  }
  
  // Test a tool
  async testTool(id: string, parameters: any = {}): Promise<any> {
    const response = await fetch(`${API_URL}/api/v1/tools/${id}/test`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify({ parameters })
    });

    return this.handleResponse<any>(response);
  }
  
  // Document Management
  
  // Get all documents
  async getDocuments(page: number = 0, limit: number = 10, fileType?: string): Promise<DocumentResponse> {
    let url = `${API_URL}/api/v1/documents?skip=${page * limit}&limit=${limit}`;
    if (fileType) url += `&file_type=${encodeURIComponent(fileType)}`;
    
    const response = await fetch(url, {
      headers: this.getHeaders()
    });

    return this.handleResponse<DocumentResponse>(response);
  }
  
  // Get a specific document
  async getDocument(id: string): Promise<Document> {
    const response = await fetch(`${API_URL}/api/v1/documents/${id}`, {
      headers: this.getHeaders()
    });

    return this.handleResponse<Document>(response);
  }
  
  // Create a document (manual entry)
  async createDocument(document: Document): Promise<Document> {
    const response = await fetch(`${API_URL}/api/v1/documents`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify(document)
    });

    return this.handleResponse<Document>(response);
  }
  
  // Upload a document file
  async uploadDocument(file: File, title: string): Promise<Document> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('title', title);
    
    const response = await fetch(`${API_URL}/api/v1/documents/upload`, {
      method: 'POST',
      headers: {
        'Authorization': this.token ? `Bearer ${this.token}` : ''
      },
      body: formData
    });

    return this.handleResponse<Document>(response);
  }
  
  // Extract text from a document
  async extractDocumentText(id: string): Promise<{ text: string, document_id: string }> {
    const response = await fetch(`${API_URL}/api/v1/documents/${id}/extract`, {
      method: 'POST',
      headers: this.getHeaders()
    });

    return this.handleResponse<{ text: string, document_id: string }>(response);
  }
  
  // Delete a document
  async deleteDocument(id: string): Promise<void> {
    const response = await fetch(`${API_URL}/api/v1/documents/${id}`, {
      method: 'DELETE',
      headers: this.getHeaders()
    });

    if (!response.ok) {
      try {
        const errorData = await response.json();
        throw new Error(errorData.detail || `API error: ${response.status}`);
      } catch (e) {
        throw new Error(`API error: ${response.status}`);
      }
    }
  }
  
  // Vector Database Management
  
  // Get all vector databases
  async getVectorDatabases(page: number = 0, limit: number = 10, dbType?: string): Promise<VectorDatabaseResponse> {
    let url = `${API_URL}/api/v1/vector-dbs?skip=${page * limit}&limit=${limit}`;
    if (dbType) url += `&db_type=${encodeURIComponent(dbType)}`;
    
    const response = await fetch(url, {
      headers: this.getHeaders()
    });

    return this.handleResponse<VectorDatabaseResponse>(response);
  }
  
  // Get a specific vector database
  async getVectorDatabase(id: string): Promise<VectorDatabase> {
    const response = await fetch(`${API_URL}/api/v1/vector-dbs/${id}`, {
      headers: this.getHeaders()
    });

    return this.handleResponse<VectorDatabase>(response);
  }
  
  // Create a vector database
  async createVectorDatabase(db: VectorDatabase): Promise<VectorDatabase> {
    const response = await fetch(`${API_URL}/api/v1/vector-dbs`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify(db)
    });

    return this.handleResponse<VectorDatabase>(response);
  }
  
  // Delete a vector database
  async deleteVectorDatabase(id: string): Promise<void> {
    const response = await fetch(`${API_URL}/api/v1/vector-dbs/${id}`, {
      method: 'DELETE',
      headers: this.getHeaders()
    });

    if (!response.ok) {
      try {
        const errorData = await response.json();
        throw new Error(errorData.detail || `API error: ${response.status}`);
      } catch (e) {
        throw new Error(`API error: ${response.status}`);
      }
    }
  }
  
  // Get available vector database types
  async getVectorDatabaseTypes(): Promise<VectorDBType[]> {
    const response = await fetch(`${API_URL}/api/v1/vector-dbs/types`, {
      headers: this.getHeaders()
    });

    return this.handleResponse<VectorDBType[]>(response);
  }
  
  // Embedding Management
  
  // Get all embeddings
  async getEmbeddings(page: number = 0, limit: number = 10, documentId?: string, vectorDbId?: string): Promise<EmbeddingResponse> {
    let url = `${API_URL}/api/v1/embeddings?skip=${page * limit}&limit=${limit}`;
    if (documentId) url += `&document_id=${encodeURIComponent(documentId)}`;
    if (vectorDbId) url += `&vector_db_id=${encodeURIComponent(vectorDbId)}`;
    
    const response = await fetch(url, {
      headers: this.getHeaders()
    });

    return this.handleResponse<EmbeddingResponse>(response);
  }
  
  // Get a specific embedding
  async getEmbedding(id: string): Promise<Embedding> {
    const response = await fetch(`${API_URL}/api/v1/embeddings/${id}`, {
      headers: this.getHeaders()
    });

    return this.handleResponse<Embedding>(response);
  }
  
  // Create an embedding (starts async task)
  async createEmbedding(request: EmbeddingRequest): Promise<EmbeddingTaskResponse> {
    const response = await fetch(`${API_URL}/api/v1/embeddings`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify(request)
    });

    return this.handleResponse<EmbeddingTaskResponse>(response);
  }
  
  // Check embedding task status
  async checkEmbeddingTaskStatus(taskId: string): Promise<TaskStatus> {
    const response = await fetch(`${API_URL}/api/v1/embeddings/tasks/${taskId}`, {
      headers: this.getHeaders()
    });

    return this.handleResponse<TaskStatus>(response);
  }
  
  // Delete an embedding
  async deleteEmbedding(id: string): Promise<void> {
    const response = await fetch(`${API_URL}/api/v1/embeddings/${id}`, {
      method: 'DELETE',
      headers: this.getHeaders()
    });

    if (!response.ok) {
      try {
        const errorData = await response.json();
        throw new Error(errorData.detail || `API error: ${response.status}`);
      } catch (e) {
        throw new Error(`API error: ${response.status}`);
      }
    }
  }
  
  // Get available embedding models
  async getEmbeddingModels(): Promise<EmbeddingModel[]> {
    const response = await fetch(`${API_URL}/api/v1/embeddings/models`, {
      headers: this.getHeaders()
    });

    return this.handleResponse<EmbeddingModel[]>(response);
  }

  // RAG System Management
  
  // Get all RAG systems
  async getRAGSystems(page: number = 0, limit: number = 10): Promise<RAGSystemResponse> {
    const url = `${API_URL}/api/v1/rag-systems?skip=${page * limit}&limit=${limit}`;
    
    const response = await fetch(url, {
      headers: this.getHeaders()
    });

    return this.handleResponse<RAGSystemResponse>(response);
  }
  
  // Get a specific RAG system
  async getRAGSystem(id: string): Promise<RAGSystem> {
    const response = await fetch(`${API_URL}/api/v1/rag-systems/${id}`, {
      headers: this.getHeaders()
    });

    return this.handleResponse<RAGSystem>(response);
  }
  
  // Create a RAG system
  async createRAGSystem(ragSystem: RAGSystem): Promise<RAGSystem> {
    const response = await fetch(`${API_URL}/api/v1/rag-systems`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify(ragSystem)
    });

    return this.handleResponse<RAGSystem>(response);
  }
  
  // Update a RAG system
  async updateRAGSystem(id: string, ragSystem: Partial<RAGSystem>): Promise<RAGSystem> {
    const response = await fetch(`${API_URL}/api/v1/rag-systems/${id}`, {
      method: 'PUT',
      headers: this.getHeaders(),
      body: JSON.stringify(ragSystem)
    });

    return this.handleResponse<RAGSystem>(response);
  }
  
  // Delete a RAG system
  async deleteRAGSystem(id: string): Promise<void> {
    const response = await fetch(`${API_URL}/api/v1/rag-systems/${id}`, {
      method: 'DELETE',
      headers: this.getHeaders()
    });

    if (!response.ok) {
      try {
        const errorData = await response.json();
        throw new Error(errorData.detail || `API error: ${response.status}`);
      } catch (e) {
        throw new Error(`API error: ${response.status}`);
      }
    }
  }
  
  // Test a RAG system
  async testRAGSystem(id: string, query: string): Promise<any> {
    const response = await fetch(`${API_URL}/api/v1/rag-systems/${id}/test`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify({ text: query })
    });

    return this.handleResponse<any>(response);
  }
}

// Export singleton instance of the API client
export const api = new ApiClient();
