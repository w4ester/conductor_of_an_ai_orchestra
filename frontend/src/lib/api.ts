// API client for interacting with backend
// Uses fetch API to make HTTP requests

// Backend URL - replace with environment variable in production
const API_URL = 'http://localhost:8000';

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
  created_by?: string;
  created_at?: string;
  updated_at?: string;
}

// Interface for Tool
export interface Tool {
  id?: string;
  name: string;
  description: string;
  code: string;
  language: string;
  created_by?: string;
  created_at?: string;
  updated_at?: string;
}

// Interface for Document
export interface Document {
  id?: string;
  title: string;
  content: string;
  file_type: string;
  created_by?: string;
  created_at?: string;
}

// Interface for RAG System
export interface RAGSystem {
  id?: string;
  name: string;
  description: string;
  embedding_model: string;
  documents: string[];
  created_by?: string;
  created_at?: string;
  updated_at?: string;
}

// Interface for Vector Database
export interface VectorDatabase {
  id?: string;
  name: string;
  type: string;
  connection_string?: string;
  created_by?: string;
  created_at?: string;
  updated_at?: string;
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
  created_by?: string;
  created_at?: string;
  chunks?: any[];
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

  // Login and get token
  async login(credentials: LoginCredentials): Promise<AuthToken> {
    // Convert credentials to form data format required by OAuth2
    const formData = new URLSearchParams();
    formData.append('username', credentials.username);
    formData.append('password', credentials.password);

    const response = await fetch(`${API_URL}/token`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      },
      body: formData
    });

    if (!response.ok) {
      throw new Error('Login failed');
    }

    const data = await response.json();
    this.setToken(data.access_token);
    return data;
  }

  // Get current user
  async getCurrentUser(): Promise<User> {
    const response = await fetch(`${API_URL}/api/users/me`, {
      headers: this.getHeaders()
    });

    if (!response.ok) {
      throw new Error('Failed to get user');
    }

    return response.json();
  }

  // Get list of available models
  async getModels(): Promise<OllamaModel[]> {
    const response = await fetch(`${API_URL}/api/models`, {
      headers: this.getHeaders()
    });

    if (!response.ok) {
      throw new Error('Failed to get models');
    }

    return response.json();
  }

  // Generate text with a model
  async generate(requestData: any): Promise<any> {
    const response = await fetch(`${API_URL}/api/generate`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify(requestData)
    });

    if (!response.ok) {
      throw new Error('Generation failed');
    }

    return response.json();
  }
  
  // Chat with a model
  async chat(requestData: any): Promise<any> {
    const response = await fetch(`${API_URL}/api/chat`, {
      method: 'POST', 
      headers: this.getHeaders(),
      body: JSON.stringify(requestData)
    });
    
    if (!response.ok) {
      throw new Error('Chat failed: ' + (await response.text()));
    }
    
    return response.json();
  }
  
  // Create or update a model with a Modelfile
  async createModel(name: string, modelfile: string): Promise<any> {
    const response = await fetch(`${API_URL}/api/models/create`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify({
        name,
        modelfile
      })
    });

    if (!response.ok) {
      throw new Error('Model creation failed');
    }

    return response.json();
  }
  
  // Get a model's Modelfile
  async getModelfile(name: string): Promise<string> {
    const response = await fetch(`${API_URL}/api/models/${name}/modelfile`, {
      headers: this.getHeaders()
    });

    if (!response.ok) {
      throw new Error('Failed to get modelfile');
    }

    const data = await response.json();
    return data.modelfile || '';
  }
  
  // Delete a model
  async deleteModel(name: string): Promise<void> {
    const response = await fetch(`${API_URL}/api/models/${name}`, {
      method: 'DELETE',
      headers: this.getHeaders()
    });

    if (!response.ok) {
      throw new Error('Failed to delete model');
    }
  }

  // Get embeddings for a text
  async getEmbeddings(model: string, text: string): Promise<any> {
    const response = await fetch(`${API_URL}/api/embeddings`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify({
        model,
        prompt: text
      })
    });

    if (!response.ok) {
      throw new Error('Failed to get embeddings');
    }

    return response.json();
  }

  // Check if API is available
  async healthCheck(): Promise<{ status: string }> {
    const response = await fetch(`${API_URL}/api/health`);

    if (!response.ok) {
      throw new Error('API health check failed');
    }

    return response.json();
  }
  
  // Prompt Management
  
  // Get all prompts
  async getPrompts(): Promise<Prompt[]> {
    const response = await fetch(`${API_URL}/api/prompts`, {
      headers: this.getHeaders()
    });

    if (!response.ok) {
      throw new Error('Failed to get prompts');
    }

    return response.json();
  }
  
  // Get a specific prompt
  async getPrompt(id: string): Promise<Prompt> {
    const response = await fetch(`${API_URL}/api/prompts/${id}`, {
      headers: this.getHeaders()
    });

    if (!response.ok) {
      throw new Error('Failed to get prompt');
    }

    return response.json();
  }
  
  // Create a new prompt
  async createPrompt(prompt: Prompt): Promise<Prompt> {
    const response = await fetch(`${API_URL}/api/prompts`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify(prompt)
    });

    if (!response.ok) {
      throw new Error('Failed to create prompt');
    }

    return response.json();
  }
  
  // Update a prompt
  async updatePrompt(id: string, prompt: Prompt): Promise<Prompt> {
    const response = await fetch(`${API_URL}/api/prompts/${id}`, {
      method: 'PUT',
      headers: this.getHeaders(),
      body: JSON.stringify(prompt)
    });

    if (!response.ok) {
      throw new Error('Failed to update prompt');
    }

    return response.json();
  }
  
  // Delete a prompt
  async deletePrompt(id: string): Promise<void> {
    const response = await fetch(`${API_URL}/api/prompts/${id}`, {
      method: 'DELETE',
      headers: this.getHeaders()
    });

    if (!response.ok) {
      throw new Error('Failed to delete prompt');
    }
  }
  
  // Tool Management
  
  // Get all tools
  async getTools(): Promise<Tool[]> {
    const response = await fetch(`${API_URL}/api/tools`, {
      headers: this.getHeaders()
    });

    if (!response.ok) {
      throw new Error('Failed to get tools');
    }

    return response.json();
  }
  
  // Get a specific tool
  async getTool(id: string): Promise<Tool> {
    const response = await fetch(`${API_URL}/api/tools/${id}`, {
      headers: this.getHeaders()
    });

    if (!response.ok) {
      throw new Error('Failed to get tool');
    }

    return response.json();
  }
  
  // Create a new tool
  async createTool(tool: Tool): Promise<Tool> {
    const response = await fetch(`${API_URL}/api/tools`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify(tool)
    });

    if (!response.ok) {
      throw new Error('Failed to create tool');
    }

    return response.json();
  }
  
  // Update a tool
  async updateTool(id: string, tool: Tool): Promise<Tool> {
    const response = await fetch(`${API_URL}/api/tools/${id}`, {
      method: 'PUT',
      headers: this.getHeaders(),
      body: JSON.stringify(tool)
    });

    if (!response.ok) {
      throw new Error('Failed to update tool');
    }

    return response.json();
  }
  
  // Delete a tool
  async deleteTool(id: string): Promise<void> {
    const response = await fetch(`${API_URL}/api/tools/${id}`, {
      method: 'DELETE',
      headers: this.getHeaders()
    });

    if (!response.ok) {
      throw new Error('Failed to delete tool');
    }
  }
  
  // Test a tool
  async testTool(id: string, parameters: any = {}): Promise<any> {
    const response = await fetch(`${API_URL}/api/tools/${id}/test`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify({ parameters })
    });

    if (!response.ok) {
      throw new Error('Failed to test tool');
    }

    return response.json();
  }
  
  // Document Management
  
  // Get all documents
  async getDocuments(): Promise<Document[]> {
    const response = await fetch(`${API_URL}/api/documents`, {
      headers: this.getHeaders()
    });

    if (!response.ok) {
      throw new Error('Failed to get documents');
    }

    return response.json();
  }
  
  // Get a specific document
  async getDocument(id: string): Promise<Document> {
    const response = await fetch(`${API_URL}/api/documents/${id}`, {
      headers: this.getHeaders()
    });

    if (!response.ok) {
      throw new Error('Failed to get document');
    }

    return response.json();
  }
  
  // Create a document (manual entry)
  async createDocument(document: Document): Promise<Document> {
    const response = await fetch(`${API_URL}/api/documents`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify(document)
    });

    if (!response.ok) {
      throw new Error('Failed to create document');
    }

    return response.json();
  }
  
  // Upload a document file
  async uploadDocument(file: File, title: string): Promise<Document> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('title', title);
    
    const response = await fetch(`${API_URL}/api/documents/upload`, {
      method: 'POST',
      headers: {
        'Authorization': this.token ? `Bearer ${this.token}` : ''
      },
      body: formData
    });

    if (!response.ok) {
      throw new Error('Failed to upload document');
    }

    return response.json();
  }
  
  // Extract text from a document
  async extractDocumentText(id: string): Promise<{ text: string, document_id: string }> {
    const response = await fetch(`${API_URL}/api/documents/${id}/extract`, {
      method: 'POST',
      headers: this.getHeaders()
    });

    if (!response.ok) {
      throw new Error('Failed to extract document text');
    }

    return response.json();
  }
  
  // Delete a document
  async deleteDocument(id: string): Promise<void> {
    const response = await fetch(`${API_URL}/api/documents/${id}`, {
      method: 'DELETE',
      headers: this.getHeaders()
    });

    if (!response.ok) {
      throw new Error('Failed to delete document');
    }
  }
  
  // Vector Database Management
  
  // Get all vector databases
  async getVectorDatabases(): Promise<VectorDatabase[]> {
    const response = await fetch(`${API_URL}/api/vector-dbs`, {
      headers: this.getHeaders()
    });

    if (!response.ok) {
      throw new Error('Failed to get vector databases');
    }

    return response.json();
  }
  
  // Get a specific vector database
  async getVectorDatabase(id: string): Promise<VectorDatabase> {
    const response = await fetch(`${API_URL}/api/vector-dbs/${id}`, {
      headers: this.getHeaders()
    });

    if (!response.ok) {
      throw new Error('Failed to get vector database');
    }

    return response.json();
  }
  
  // Create a vector database
  async createVectorDatabase(db: VectorDatabase): Promise<VectorDatabase> {
    const response = await fetch(`${API_URL}/api/vector-dbs`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify(db)
    });

    if (!response.ok) {
      throw new Error('Failed to create vector database');
    }

    return response.json();
  }
  
  // Delete a vector database
  async deleteVectorDatabase(id: string): Promise<void> {
    const response = await fetch(`${API_URL}/api/vector-dbs/${id}`, {
      method: 'DELETE',
      headers: this.getHeaders()
    });

    if (!response.ok) {
      throw new Error('Failed to delete vector database');
    }
  }
  
  // Get available vector database types
  async getVectorDatabaseTypes(): Promise<VectorDBType[]> {
    const response = await fetch(`${API_URL}/api/vector-db-types`, {
      headers: this.getHeaders()
    });

    if (!response.ok) {
      throw new Error('Failed to get vector database types');
    }

    return response.json();
  }
  
  // Embedding Management
  
  // Get all embeddings
  async getEmbeddings(): Promise<Embedding[]> {
    const response = await fetch(`${API_URL}/api/embeddings`, {
      headers: this.getHeaders()
    });

    if (!response.ok) {
      throw new Error('Failed to get embeddings');
    }

    return response.json();
  }
  
  // Get a specific embedding
  async getEmbedding(id: string): Promise<Embedding> {
    const response = await fetch(`${API_URL}/api/embeddings/${id}`, {
      headers: this.getHeaders()
    });

    if (!response.ok) {
      throw new Error('Failed to get embedding');
    }

    return response.json();
  }
  
  // Create an embedding
  async createEmbedding(request: EmbeddingRequest): Promise<Embedding> {
    const response = await fetch(`${API_URL}/api/embeddings`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify(request)
    });

    if (!response.ok) {
      throw new Error('Failed to create embedding');
    }

    return response.json();
  }
  
  // Delete an embedding
  async deleteEmbedding(id: string): Promise<void> {
    const response = await fetch(`${API_URL}/api/embeddings/${id}`, {
      method: 'DELETE',
      headers: this.getHeaders()
    });

    if (!response.ok) {
      throw new Error('Failed to delete embedding');
    }
  }
  
  // Get available embedding models
  async getEmbeddingModels(): Promise<EmbeddingModel[]> {
    const response = await fetch(`${API_URL}/api/embedding-models`, {
      headers: this.getHeaders()
    });

    if (!response.ok) {
      throw new Error('Failed to get embedding models');
    }

    return response.json();
  }
}

// Export singleton instance of the API client
export const api = new ApiClient();