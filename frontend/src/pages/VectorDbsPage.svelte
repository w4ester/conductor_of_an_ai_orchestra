<script lang="ts">
  import { onMount } from 'svelte';
  import { api } from '../lib/api';
  import { vectorDbsStore } from '../lib/store';
  
  // State
  let loading = true;
  let error = '';
  
  // Load vector databases
  onMount(async () => {
    try {
      const dbs = await api.getVectorDatabases();
      vectorDbsStore.set(dbs);
      loading = false;
    } catch (err) {
      console.error('Failed to load vector databases:', err);
      error = 'Failed to load vector databases. Please try again.';
      loading = false;
    }
  });
  
  // Delete vector database
  async function deleteVectorDb(id: string, name: string) {
    if (!confirm(`Are you sure you want to delete the vector database "${name}"? This cannot be undone.`)) {
      return;
    }
    
    try {
      await api.deleteVectorDatabase(id);
      
      // Update store by removing the deleted vector database
      vectorDbsStore.update(dbs => dbs.filter(db => db.id !== id));
    } catch (err) {
      console.error('Failed to delete vector database:', err);
      error = `Failed to delete vector database: ${err.message}`;
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
    <h1 style="font-size: 1.5rem; font-weight: bold;">Vector Databases</h1>
    <a href="#/vector-dbs/create" style="background-color: #2563eb; color: white; padding: 0.5rem 1rem; border-radius: 0.25rem; font-size: 0.875rem; text-decoration: none; display: flex; align-items: center;">
      <span style="margin-right: 0.25rem;">+</span> Create Vector Database
    </a>
  </div>
  
  {#if error}
    <div style="background-color: #fee2e2; border: 1px solid #f87171; color: #b91c1c; padding: 0.75rem 1rem; border-radius: 0.25rem; margin-bottom: 1rem;" role="alert">
      <span>{error}</span>
    </div>
  {/if}
  
  <!-- Vector Databases List -->
  {#if loading}
    <div style="display: flex; justify-content: center; padding: 2rem;">
      <p>Loading vector databases...</p>
    </div>
  {:else if $vectorDbsStore.length === 0}
    <div style="background-color: white; padding: 2rem; text-align: center; border-radius: 0.5rem; box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);">
      <p style="color: #6b7280;">No vector databases found.</p>
      <a href="#/vector-dbs/create" style="display: inline-block; margin-top: 1rem; background-color: #2563eb; color: white; padding: 0.5rem 1rem; border-radius: 0.25rem; font-size: 0.875rem; text-decoration: none;">
        Create your first vector database
      </a>
    </div>
  {:else}
    <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 1rem;">
      {#each $vectorDbsStore as db}
        <div style="background-color: white; padding: 1.5rem; border-radius: 0.5rem; box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06); display: flex; flex-direction: column;">
          <div style="margin-bottom: 0.75rem;">
            <h2 style="font-size: 1.125rem; font-weight: 500;">{db.name}</h2>
            <div style="margin-top: 0.25rem;">
              <span style="background-color: #f3f4f6; padding: 0.25rem 0.5rem; border-radius: 0.25rem; font-size: 0.75rem; text-transform: uppercase;">
                {db.type}
              </span>
            </div>
          </div>
          
          <div style="margin-bottom: 1rem; font-size: 0.75rem; color: #6b7280; flex-grow: 1;">
            <p>Created: {formatDate(db.created_at)}</p>
            {#if db.updated_at && db.updated_at !== db.created_at}
              <p>Updated: {formatDate(db.updated_at)}</p>
            {/if}
            {#if db.connection_string}
              <p style="margin-top: 0.5rem; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">
                Connection: {db.connection_string}
              </p>
            {/if}
          </div>
          
          <div style="display: flex; gap: 0.5rem;">
            <a 
              href="#/vector-dbs/edit/{db.id}" 
              style="flex: 1; text-align: center; padding: 0.375rem 0; font-size: 0.875rem; background-color: #eff6ff; color: #2563eb; border-radius: 0.25rem; text-decoration: none;"
            >
              Edit
            </a>
            <button 
              on:click={() => deleteVectorDb(db.id, db.name)}
              style="flex: 1; text-align: center; padding: 0.375rem 0; font-size: 0.875rem; background-color: #fee2e2; color: #b91c1c; border-radius: 0.25rem; border: none; cursor: pointer;"
            >
              Delete
            </button>
          </div>
        </div>
      {/each}
    </div>
  {/if}
  
  <!-- Info Section -->
  <div style="margin-top: 2rem; background-color: white; padding: 1.5rem; border-radius: 0.5rem; box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);">
    <h2 style="font-size: 1.25rem; font-weight: 500; margin-bottom: 1rem;">About Vector Databases</h2>
    
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1.5rem;">
      <div>
        <h3 style="font-size: 1rem; font-weight: 500; margin-bottom: 0.5rem;">What are Vector Databases?</h3>
        <p style="font-size: 0.875rem; color: #4b5563;">
          Vector databases are specialized storage systems designed to efficiently store, index, and query high-dimensional vector data generated by embedding models.
        </p>
      </div>
      
      <div>
        <h3 style="font-size: 1rem; font-weight: 500; margin-bottom: 0.5rem;">Why Use Them?</h3>
        <p style="font-size: 0.875rem; color: #4b5563;">
          They enable fast similarity search for RAG systems, which traditional databases can't efficiently perform. This allows semantic matching of documents to queries.
        </p>
      </div>
      
      <div>
        <h3 style="font-size: 1rem; font-weight: 500; margin-bottom: 0.5rem;">Setting Up</h3>
        <p style="font-size: 0.875rem; color: #4b5563;">
          You can use our built-in in-memory vector database for prototyping, or connect to external solutions like Chroma, Pinecone, or Qdrant for production environments.
        </p>
      </div>
    </div>
    
    <div style="margin-top: 1.5rem; text-align: center;">
      <a href="#/embeddings" style="display: inline-block; padding: 0.5rem 1rem; background-color: #eff6ff; color: #1e40af; border-radius: 0.25rem; font-size: 0.875rem; text-decoration: none;">
        Manage Embeddings
      </a>
    </div>
  </div>
</div>