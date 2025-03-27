<script lang="ts">
  import { onMount } from 'svelte';
  import { api } from '../lib/api';
  import { documentsStore, vectorDbsStore, embeddingsStore, embeddingModelsStore } from '../lib/store';
  import type { Document, VectorDatabase, EmbeddingModel, EmbeddingRequest } from '../lib/api';
  
  // State
  let documents: Document[] = [];
  let vectorDbs: VectorDatabase[] = [];
  let embeddingModels: EmbeddingModel[] = [];
  let selectedDocumentId = '';
  let selectedVectorDbId = '';
  let selectedModel = '';
  let chunkSize = 1000;
  let chunkOverlap = 200;
  let isProcessing = false;
  let error = '';
  let success = '';
  let processingProgress = 0;
  
  // Load data
  onMount(async () => {
    try {
      // Load documents
      documents = await api.getDocuments();
      documentsStore.set(documents);
      
      // Load vector databases
      vectorDbs = await api.getVectorDatabases();
      vectorDbsStore.set(vectorDbs);
      
      // Load embedding models
      embeddingModels = await api.getEmbeddingModels();
      embeddingModelsStore.set(embeddingModels);
      
      // Set defaults if available
      if (embeddingModels.length > 0) {
        selectedModel = embeddingModels[0].name;
      }
      
      if (vectorDbs.length > 0) {
        selectedVectorDbId = vectorDbs[0].id;
      }
    } catch (err) {
      console.error('Failed to load data:', err);
      error = 'Failed to load data. Please try again.';
    }
  });
  
  // Get selected document info
  $: selectedDocument = documents.find(doc => doc.id === selectedDocumentId);
  
  // Get selected vector DB info
  $: selectedVectorDb = vectorDbs.find(db => db.id === selectedVectorDbId);
  
  // Get selected model info
  $: selectedModelInfo = embeddingModels.find(model => model.name === selectedModel);
  
  // Create embedding
  async function createEmbedding() {
    if (!selectedDocumentId) {
      error = 'Please select a document';
      return;
    }
    
    if (!selectedVectorDbId) {
      error = 'Please select a vector database';
      return;
    }
    
    if (!selectedModel) {
      error = 'Please select an embedding model';
      return;
    }
    
    try {
      isProcessing = true;
      error = '';
      success = '';
      processingProgress = 10; // Start progress
      
      // Create embedding request
      const request: EmbeddingRequest = {
        document_id: selectedDocumentId,
        vector_db_id: selectedVectorDbId,
        model: selectedModel,
        chunk_size: chunkSize,
        chunk_overlap: chunkOverlap
      };
      
      processingProgress = 30; // Processing
      
      // Create embedding
      const embedding = await api.createEmbedding(request);
      
      processingProgress = 90; // Almost done
      
      // Update embeddings store
      const embeddings = await api.getEmbeddings();
      embeddingsStore.set(embeddings);
      
      processingProgress = 100; // Complete
      success = `Embedding created successfully for document "${selectedDocument?.title}"`;
      
      // Reset form
      selectedDocumentId = '';
      chunkSize = 1000;
      chunkOverlap = 200;
    } catch (err) {
      console.error('Failed to create embedding:', err);
      error = `Failed to create embedding: ${err.message}`;
    } finally {
      isProcessing = false;
      // Reset progress after a delay
      setTimeout(() => {
        processingProgress = 0;
      }, 3000);
    }
  }
  
  // Cancel
  function cancel() {
    window.history.back();
  }
  
  // Get file icon based on extension
  function getFileIcon(fileType: string) {
    switch (fileType?.toLowerCase()) {
      case 'pdf':
        return '📄';
      case 'docx':
      case 'doc':
        return '📝';
      case 'txt':
        return '📃';
      case 'csv':
        return '📊';
      case 'md':
        return '📑';
      default:
        return '📁';
    }
  }
</script>

<div style="padding: 1.5rem;">
  <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem;">
    <h1 style="font-size: 1.5rem; font-weight: bold;">Create Embeddings</h1>
    <button 
      on:click={cancel}
      style="padding: 0.5rem 1rem; border: 1px solid #d1d5db; border-radius: 0.25rem; background-color: white;"
    >
      Cancel
    </button>
  </div>
  
  {#if error}
    <div style="background-color: #fee2e2; border: 1px solid #f87171; color: #b91c1c; padding: 0.75rem 1rem; border-radius: 0.25rem; margin-bottom: 1rem;" role="alert">
      <span>{error}</span>
    </div>
  {/if}
  
  {#if success}
    <div style="background-color: #d1fae5; border: 1px solid #34d399; color: #065f46; padding: 0.75rem 1rem; border-radius: 0.25rem; margin-bottom: 1rem;" role="alert">
      <span>{success}</span>
    </div>
  {/if}
  
  <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem;">
    <!-- Embedding Configuration Form -->
    <div style="background-color: white; padding: 1.5rem; border-radius: 0.5rem; box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);">
      <h2 style="font-size: 1.125rem; font-weight: 500; margin-bottom: 1rem;">Embedding Configuration</h2>
      
      <!-- Document Selection -->
      <div style="margin-bottom: 1.5rem;">
        <label for="document" style="display: block; font-size: 0.875rem; font-weight: 500; margin-bottom: 0.25rem;">
          Select Document
        </label>
        <select 
          id="document" 
          bind:value={selectedDocumentId}
          style="width: 100%; padding: 0.5rem 0.75rem; border: 1px solid #d1d5db; border-radius: 0.375rem; box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);"
          disabled={isProcessing}
        >
          <option value="">Select a document</option>
          {#each documents as document}
            <option value={document.id}>{document.title} ({document.file_type.toUpperCase()})</option>
          {/each}
        </select>
        {#if documents.length === 0}
          <p style="font-size: 0.75rem; color: #ef4444; margin-top: 0.25rem;">
            No documents found. <a href="#/documents/upload" style="color: #2563eb;">Upload a document</a> first.
          </p>
        {/if}
      </div>
      
      <!-- Vector Database Selection -->
      <div style="margin-bottom: 1.5rem;">
        <label for="vector_db" style="display: block; font-size: 0.875rem; font-weight: 500; margin-bottom: 0.25rem;">
          Vector Database
        </label>
        <select 
          id="vector_db" 
          bind:value={selectedVectorDbId}
          style="width: 100%; padding: 0.5rem 0.75rem; border: 1px solid #d1d5db; border-radius: 0.375rem; box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);"
          disabled={isProcessing}
        >
          <option value="">Select a vector database</option>
          {#each vectorDbs as db}
            <option value={db.id}>{db.name} ({db.type})</option>
          {/each}
        </select>
        {#if vectorDbs.length === 0}
          <p style="font-size: 0.75rem; color: #ef4444; margin-top: 0.25rem;">
            No vector databases found. <a href="#/vector-dbs/create" style="color: #2563eb;">Create a vector database</a> first.
          </p>
        {/if}
      </div>
      
      <!-- Embedding Model Selection -->
      <div style="margin-bottom: 1.5rem;">
        <label for="model" style="display: block; font-size: 0.875rem; font-weight: 500; margin-bottom: 0.25rem;">
          Embedding Model
        </label>
        <select 
          id="model" 
          bind:value={selectedModel}
          style="width: 100%; padding: 0.5rem 0.75rem; border: 1px solid #d1d5db; border-radius: 0.375rem; box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);"
          disabled={isProcessing}
        >
          <option value="">Select an embedding model</option>
          {#each embeddingModels as model}
            <option value={model.name}>{model.name} ({model.dimensions} dimensions)</option>
          {/each}
        </select>
        {#if selectedModelInfo}
          <p style="font-size: 0.75rem; color: #6b7280; margin-top: 0.25rem;">
            {selectedModelInfo.description}
          </p>
        {/if}
      </div>
      
      <!-- Chunking Parameters -->
      <div style="margin-bottom: 1.5rem;">
        <h3 style="font-size: 0.875rem; font-weight: 500; margin-bottom: 0.75rem;">Text Chunking Parameters</h3>
        
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
          <div>
            <label for="chunk_size" style="display: block; font-size: 0.75rem; margin-bottom: 0.25rem;">
              Chunk Size
            </label>
            <input 
              type="number" 
              id="chunk_size" 
              bind:value={chunkSize}
              min="100"
              max="5000"
              step="100"
              style="width: 100%; padding: 0.5rem 0.75rem; border: 1px solid #d1d5db; border-radius: 0.375rem; box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);"
              disabled={isProcessing}
            />
          </div>
          
          <div>
            <label for="chunk_overlap" style="display: block; font-size: 0.75rem; margin-bottom: 0.25rem;">
              Chunk Overlap
            </label>
            <input 
              type="number" 
              id="chunk_overlap" 
              bind:value={chunkOverlap}
              min="0"
              max="1000"
              step="50"
              style="width: 100%; padding: 0.5rem 0.75rem; border: 1px solid #d1d5db; border-radius: 0.375rem; box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);"
              disabled={isProcessing}
            />
          </div>
        </div>
        
        <p style="font-size: 0.75rem; color: #6b7280; margin-top: 0.5rem;">
          Text will be split into chunks of approximately {chunkSize} characters with {chunkOverlap} characters of overlap between chunks.
        </p>
      </div>
      
      {#if processingProgress > 0}
        <div style="margin-bottom: 1.5rem;">
          <div style="width: 100%; background-color: #e5e7eb; height: 0.5rem; border-radius: 9999px; overflow: hidden;">
            <div 
              style={`width: ${processingProgress}%; background-color: #2563eb; height: 100%; transition: width 0.3s ease;`}
            ></div>
          </div>
          <p style="font-size: 0.75rem; color: #6b7280; margin-top: 0.25rem; text-align: center;">
            {processingProgress === 100 ? 'Processing complete!' : 'Processing document...'}
          </p>
        </div>
      {/if}
      
      <div>
        <button 
          on:click={createEmbedding}
          disabled={isProcessing || !selectedDocumentId || !selectedVectorDbId || !selectedModel}
          style="width: 100%; padding: 0.5rem 1rem; border-radius: 0.25rem; background-color: #2563eb; color: white; opacity: ${isProcessing || !selectedDocumentId || !selectedVectorDbId || !selectedModel ? '0.7' : '1'};"
        >
          {isProcessing ? 'Processing...' : 'Create Embedding'}
        </button>
      </div>
    </div>
    
    <!-- Document Preview -->
    <div>
      {#if selectedDocument}
        <div style="background-color: white; padding: 1.5rem; border-radius: 0.5rem; box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06); margin-bottom: 1.5rem;">
          <h2 style="font-size: 1.125rem; font-weight: 500; margin-bottom: 1rem;">Document Preview</h2>
          
          <div style="display: flex; align-items: center; margin-bottom: 1rem;">
            <div style="font-size: 2rem; margin-right: 1rem;">{getFileIcon(selectedDocument.file_type)}</div>
            <div>
              <h3 style="font-weight: 500;">{selectedDocument.title}</h3>
              <p style="font-size: 0.875rem; color: #6b7280;">
                Type: {selectedDocument.file_type.toUpperCase()}
              </p>
            </div>
          </div>
          
          <button
            on:click={() => api.extractDocumentText(selectedDocument.id).then(result => alert(`Preview of extracted text:\n\n${result.text.substring(0, 200)}...`))}
            style="width: 100%; padding: 0.5rem 1rem; border-radius: 0.25rem; background-color: #f3f4f6; color: #4b5563; font-size: 0.875rem;"
          >
            Preview Extracted Text
          </button>
        </div>
      {/if}
      
      <!-- Info Section -->
      <div style="background-color: white; padding: 1.5rem; border-radius: 0.5rem; box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);">
        <h2 style="font-size: 1.125rem; font-weight: 500; margin-bottom: 1rem;">About Embeddings</h2>
        
        <div style="font-size: 0.875rem; color: #4b5563;">
          <p style="margin-bottom: 1rem;">
            Embeddings are numerical representations of text that capture semantic meaning. They allow RAG systems to find documents similar to a query based on meaning rather than exact keyword matches.
          </p>
          
          <h3 style="font-weight: 500; margin-bottom: 0.5rem;">Process Overview</h3>
          <ol style="list-style: decimal; margin-left: 1.5rem; margin-bottom: 1rem;">
            <li>Document text is extracted from the file</li>
            <li>Text is split into smaller chunks with some overlap</li>
            <li>Each chunk is converted to an embedding vector using the selected model</li>
            <li>Embeddings are stored in the vector database for retrieval</li>
          </ol>
          
          <h3 style="font-weight: 500; margin-bottom: 0.5rem;">Embedding Models</h3>
          <p>
            Different embedding models offer different trade-offs between performance, accuracy, and vector dimensions. Smaller models are faster but may be less accurate for complex queries.
          </p>
        </div>
      </div>
    </div>
  </div>
</div>