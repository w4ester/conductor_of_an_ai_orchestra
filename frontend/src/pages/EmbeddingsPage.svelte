<script lang="ts">
  import { onMount } from 'svelte';
  import { api } from '../lib/api';
  import { embeddingsStore, documentsStore, vectorDbsStore } from '../lib/store';
  
  // State
  let loading = true;
  let error = '';
  let filteredDocumentId = '';
  let filteredVectorDbId = '';
  
  // Load data
  onMount(async () => {
    try {
      // Load embeddings
      const embeddings = await api.getEmbeddings();
      embeddingsStore.set(embeddings);
      
      // Load documents for reference
      const documents = await api.getDocuments();
      documentsStore.set(documents);
      
      // Load vector DBs for reference
      const vectorDbs = await api.getVectorDatabases();
      vectorDbsStore.set(vectorDbs);
      
      loading = false;
    } catch (err) {
      console.error('Failed to load embeddings:', err);
      error = 'Failed to load embeddings. Please try again.';
      loading = false;
    }
  });
  
  // Get document by ID
  function getDocumentById(id: string) {
    return $documentsStore.find(doc => doc.id === id);
  }
  
  // Get vector DB by ID
  function getVectorDbById(id: string) {
    return $vectorDbsStore.find(db => db.id === id);
  }
  
  // Filtered embeddings
  $: filteredEmbeddings = $embeddingsStore.filter(embedding => {
    if (filteredDocumentId && embedding.document_id !== filteredDocumentId) {
      return false;
    }
    if (filteredVectorDbId && embedding.vector_db_id !== filteredVectorDbId) {
      return false;
    }
    return true;
  });
  
  // Get unique document IDs from embeddings
  $: documentIds = [...new Set($embeddingsStore.map(e => e.document_id))];
  
  // Get unique vector DB IDs from embeddings
  $: vectorDbIds = [...new Set($embeddingsStore.map(e => e.vector_db_id))];
  
  // Delete embedding
  async function deleteEmbedding(id: string) {
    try {
      await api.deleteEmbedding(id);
      
      // Update store by removing the deleted embedding
      embeddingsStore.update(embeddings => embeddings.filter(e => e.id !== id));
    } catch (err) {
      console.error('Failed to delete embedding:', err);
      error = `Failed to delete embedding: ${err.message}`;
    }
  }
  
  // Format date
  function formatDate(dateString) {
    if (!dateString) return "Unknown date";
    
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
    
    if (diffDays === 0) return "Today";
    if (diffDays === 1) return "Yesterday";
    if (diffDays < 7) return `${diffDays}d ago`;
    
    return date.toLocaleDateString();
  }
</script>

<div style="padding: 1.5rem;">
  <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem;">
    <h1 style="font-size: 1.5rem; font-weight: bold;">Embeddings</h1>
    <a href="#/embeddings/create" style="background-color: #2563eb; color: white; padding: 0.5rem 1rem; border-radius: 0.25rem; font-size: 0.875rem; text-decoration: none; display: flex; align-items: center;">
      <span style="margin-right: 0.25rem;">+</span> Create Embedding
    </a>
  </div>
  
  {#if error}
    <div style="background-color: #fee2e2; border: 1px solid #f87171; color: #b91c1c; padding: 0.75rem 1rem; border-radius: 0.25rem; margin-bottom: 1rem;" role="alert">
      <span>{error}</span>
    </div>
  {/if}
  
  <!-- Filters -->
  <div style="background-color: white; padding: 1rem; border-radius: 0.5rem; box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06); margin-bottom: 1.5rem;">
    <div style="display: flex; gap: 1rem; flex-wrap: wrap;">
      <div style="flex: 1;">
        <label for="document_filter" style="display: block; font-size: 0.75rem; font-weight: 500; margin-bottom: 0.25rem;">
          Filter by Document
        </label>
        <select 
          id="document_filter" 
          bind:value={filteredDocumentId}
          style="width: 100%; padding: 0.5rem 0.75rem; border: 1px solid #d1d5db; border-radius: 0.375rem; box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);"
        >
          <option value="">All Documents</option>
          {#each documentIds as docId}
            {@const doc = getDocumentById(docId)}
            {#if doc}
              <option value={docId}>{doc.title}</option>
            {/if}
          {/each}
        </select>
      </div>
      
      <div style="flex: 1;">
        <label for="vector_db_filter" style="display: block; font-size: 0.75rem; font-weight: 500; margin-bottom: 0.25rem;">
          Filter by Vector Database
        </label>
        <select 
          id="vector_db_filter" 
          bind:value={filteredVectorDbId}
          style="width: 100%; padding: 0.5rem 0.75rem; border: 1px solid #d1d5db; border-radius: 0.375rem; box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);"
        >
          <option value="">All Vector Databases</option>
          {#each vectorDbIds as dbId}
            {@const db = getVectorDbById(dbId)}
            {#if db}
              <option value={dbId}>{db.name}</option>
            {/if}
          {/each}
        </select>
      </div>
    </div>
  </div>
  
  <!-- Embeddings List -->
  {#if loading}
    <div style="display: flex; justify-content: center; padding: 2rem;">
      <p>Loading embeddings...</p>
    </div>
  {:else if filteredEmbeddings.length === 0}
    <div style="background-color: white; padding: 2rem; text-align: center; border-radius: 0.5rem; box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);">
      <p style="color: #6b7280;">No embeddings found matching your filters.</p>
      <a href="#/embeddings/create" style="display: inline-block; margin-top: 1rem; background-color: #2563eb; color: white; padding: 0.5rem 1rem; border-radius: 0.25rem; font-size: 0.875rem; text-decoration: none;">
        Create your first embedding
      </a>
    </div>
  {:else}
    <div style="background-color: white; border-radius: 0.5rem; box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06); overflow: hidden; overflow-x: auto;">
      <table style="min-width: 100%; border-collapse: collapse;">
        <thead>
          <tr style="border-bottom: 1px solid #e5e7eb; background-color: #f9fafb;">
            <th style="padding: 0.75rem 1.5rem; text-align: left; font-size: 0.875rem; font-weight: 500; color: #4b5563;">Document</th>
            <th style="padding: 0.75rem 1.5rem; text-align: left; font-size: 0.875rem; font-weight: 500; color: #4b5563;">Vector Database</th>
            <th style="padding: 0.75rem 1.5rem; text-align: left; font-size: 0.875rem; font-weight: 500; color: #4b5563;">Model</th>
            <th style="padding: 0.75rem 1.5rem; text-align: left; font-size: 0.875rem; font-weight: 500; color: #4b5563;">Created</th>
            <th style="padding: 0.75rem 1.5rem; text-align: left; font-size: 0.875rem; font-weight: 500; color: #4b5563;">Chunks</th>
            <th style="padding: 0.75rem 1.5rem; text-align: right; font-size: 0.875rem; font-weight: 500; color: #4b5563;">Actions</th>
          </tr>
        </thead>
        <tbody>
          {#each filteredEmbeddings as embedding}
            {@const document = getDocumentById(embedding.document_id)}
            {@const vectorDb = getVectorDbById(embedding.vector_db_id)}
            <tr style="border-bottom: 1px solid #e5e7eb;">
              <td style="padding: 1rem 1.5rem;">
                {#if document}
                  <div style="font-weight: 500;">{document.title}</div>
                  <div style="font-size: 0.75rem; color: #6b7280;">{document.file_type.toUpperCase()}</div>
                {:else}
                  <span style="color: #9ca3af; font-style: italic;">Unknown document</span>
                {/if}
              </td>
              <td style="padding: 1rem 1.5rem;">
                {#if vectorDb}
                  <div style="font-weight: 500;">{vectorDb.name}</div>
                  <div style="font-size: 0.75rem; color: #6b7280;">{vectorDb.type}</div>
                {:else}
                  <span style="color: #9ca3af; font-style: italic;">Unknown database</span>
                {/if}
              </td>
              <td style="padding: 1rem 1.5rem;">
                <span style="background-color: #e0f2fe; padding: 0.25rem 0.5rem; border-radius: 0.25rem; font-size: 0.75rem;">
                  {embedding.model}
                </span>
                <div style="font-size: 0.75rem; color: #6b7280; margin-top: 0.25rem;">
                  {embedding.dimensions} dimensions
                </div>
              </td>
              <td style="padding: 1rem 1.5rem; color: #6b7280; font-size: 0.875rem;">
                {formatDate(embedding.created_at)}
              </td>
              <td style="padding: 1rem 1.5rem; color: #6b7280; font-size: 0.875rem;">
                {embedding.chunks?.length || 0} chunks
              </td>
              <td style="padding: 1rem 1.5rem; text-align: right;">
                <button 
                  on:click={() => deleteEmbedding(embedding.id)}
                  style="padding: 0.375rem 0.5rem; font-size: 0.75rem; background-color: #fee2e2; color: #b91c1c; border-radius: 0.25rem; border: none;"
                >
                  Delete
                </button>
              </td>
            </tr>
          {/each}
        </tbody>
      </table>
    </div>
  {/if}
  
  <!-- Info Section -->
  <div style="margin-top: 2rem; background-color: white; padding: 1.5rem; border-radius: 0.5rem; box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);">
    <h2 style="font-size: 1.25rem; font-weight: 500; margin-bottom: 1rem;">Building RAG Systems</h2>
    
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1.5rem;">
      <div>
        <h3 style="font-size: 1rem; font-weight: 500; margin-bottom: 0.5rem;">Embedding Pipeline</h3>
        <p style="font-size: 0.875rem; color: #4b5563;">
          Embeddings form the foundation of Retrieval Augmented Generation (RAG) systems. They enable semantic search for finding relevant documents to include as context for LLM responses.
        </p>
      </div>
      
      <div>
        <h3 style="font-size: 1rem; font-weight: 500; margin-bottom: 0.5rem;">Next Steps</h3>
        <p style="font-size: 0.875rem; color: #4b5563;">
          After creating embeddings for your documents, you can build a complete RAG system by connecting these to your LLM prompts and setting up retrieval queries.
        </p>
      </div>
      
      <div>
        <h3 style="font-size: 1rem; font-weight: 500; margin-bottom: 0.5rem;">Performance Considerations</h3>
        <p style="font-size: 0.875rem; color: #4b5563;">
          For optimal performance, experiment with different chunk sizes, embedding models, and retrieval methods to find the best configuration for your specific use case.
        </p>
      </div>
    </div>
    
    <div style="margin-top: 1.5rem; text-align: center;">
      <a href="#/rag" style="display: inline-block; padding: 0.5rem 1rem; background-color: #eff6ff; color: #1e40af; border-radius: 0.25rem; font-size: 0.875rem; text-decoration: none;">
        Create RAG System
      </a>
    </div>
  </div>
</div>