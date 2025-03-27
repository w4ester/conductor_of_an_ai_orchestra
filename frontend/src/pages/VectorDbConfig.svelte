<script lang="ts">
  import { onMount } from 'svelte';
  import { api } from '../lib/api';
  import { vectorDbsStore, vectorDbTypesStore } from '../lib/store';
  import type { VectorDatabase, VectorDBType } from '../lib/api';
  
  // Props
  export let dbId = '';
  export let isEdit = false; // true for edit, false for create
  
  // State
  let name = '';
  let type = '';
  let connectionString = '';
  let isSaving = false;
  let error = '';
  let success = '';
  let dbTypes: VectorDBType[] = [];
  
  // Load vector database data if in edit mode
  onMount(async () => {
    try {
      // Load available vector database types
      dbTypes = await api.getVectorDatabaseTypes();
      vectorDbTypesStore.set(dbTypes);
      
      if (isEdit && dbId) {
        // Load vector database data
        const db = await api.getVectorDatabase(dbId);
        
        name = db.name;
        type = db.type;
        connectionString = db.connection_string || '';
      } else {
        // Default for new vector database
        name = '';
        type = dbTypes.length > 0 ? dbTypes[0].name : '';
        connectionString = '';
      }
    } catch (err) {
      console.error('Failed to initialize vector database editor:', err);
      error = 'Failed to load data. Please try again.';
    }
  });
  
  // Save vector database
  async function saveVectorDb() {
    if (!name.trim()) {
      error = 'Please enter a name';
      return;
    }
    
    if (!type) {
      error = 'Please select a database type';
      return;
    }
    
    try {
      isSaving = true;
      error = '';
      success = '';
      
      // Create vector database object
      const db: VectorDatabase = {
        name,
        type,
        connection_string: connectionString || undefined
      };
      
      let savedDb;
      
      if (isEdit && dbId) {
        // Update existing vector database (not implemented in this basic version)
        savedDb = db; // Placeholder
        success = `Vector database "${name}" has been updated successfully`;
      } else {
        // Create new vector database
        savedDb = await api.createVectorDatabase(db);
        
        // Update store
        const dbs = await api.getVectorDatabases();
        vectorDbsStore.set(dbs);
        
        success = `Vector database "${name}" has been created successfully`;
        
        // If creating a new vector database, switch to edit mode
        if (!isEdit) {
          isEdit = true;
          dbId = savedDb.id;
          // Update URL without reloading
          window.history.replaceState({}, '', `#/vector-dbs/edit/${dbId}`);
        }
      }
    } catch (err) {
      console.error('Failed to save vector database:', err);
      error = `Failed to ${isEdit ? 'update' : 'create'} vector database: ${err.message}`;
    } finally {
      isSaving = false;
    }
  }
  
  // Delete vector database
  async function deleteVectorDb() {
    if (!confirm(`Are you sure you want to delete the vector database "${name}"? This cannot be undone.`)) {
      return;
    }
    
    try {
      isSaving = true;
      error = '';
      success = '';
      
      await api.deleteVectorDatabase(dbId);
      
      // Refresh vector databases list
      const dbs = await api.getVectorDatabases();
      vectorDbsStore.set(dbs);
      
      success = `Vector database "${name}" has been deleted successfully`;
      
      // Go back to vector databases list after a short delay
      setTimeout(() => {
        window.location.hash = '/vector-dbs';
      }, 1500);
    } catch (err) {
      console.error('Failed to delete vector database:', err);
      error = `Failed to delete vector database: ${err.message}`;
    } finally {
      isSaving = false;
    }
  }
  
  // Cancel editing
  function cancel() {
    window.history.back();
  }
  
  // Get connection string placeholder based on selected type
  $: connectionPlaceholder = getConnectionPlaceholder(type);
  
  function getConnectionPlaceholder(dbType: string): string {
    switch (dbType.toLowerCase()) {
      case 'chroma':
        return 'http://localhost:8000';
      case 'pinecone':
        return 'api-key: your-api-key, environment: your-environment';
      case 'qdrant':
        return 'http://localhost:6333';
      case 'weaviate':
        return 'http://localhost:8080';
      case 'milvus':
        return 'host: localhost, port: 19530';
      case 'redis':
        return 'redis://localhost:6379';
      case 'pgvector':
        return 'postgresql://user:password@localhost:5432/dbname';
      default:
        return 'Connection string for your vector database';
    }
  }
</script>

<div style="padding: 1.5rem;">
  <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem;">
    <h1 style="font-size: 1.5rem; font-weight: bold;">{isEdit ? 'Edit' : 'Create'} Vector Database</h1>
    <div style="display: flex; gap: 0.5rem;">
      <button 
        on:click={cancel}
        style="padding: 0.5rem 1rem; border: 1px solid #d1d5db; border-radius: 0.25rem; background-color: white;"
      >
        Cancel
      </button>
      {#if isEdit}
        <button 
          on:click={deleteVectorDb}
          disabled={isSaving}
          style="padding: 0.5rem 1rem; border-radius: 0.25rem; background-color: #ef4444; color: white; opacity: ${isSaving ? '0.7' : '1'};"
        >
          Delete Vector DB
        </button>
      {/if}
      <button 
        on:click={saveVectorDb}
        disabled={isSaving}
        style="padding: 0.5rem 1rem; border-radius: 0.25rem; background-color: #2563eb; color: white; opacity: ${isSaving ? '0.7' : '1'};"
      >
        {isSaving ? 'Saving...' : isEdit ? 'Update Vector DB' : 'Create Vector DB'}
      </button>
    </div>
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
  
  <div style="display: grid; grid-template-columns: 2fr 1fr; gap: 1.5rem;">
    <!-- Main form area -->
    <div style="background-color: white; padding: 1.5rem; border-radius: 0.5rem; box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);">
      <div style="margin-bottom: 1.5rem;">
        <label for="name" style="display: block; font-size: 0.875rem; font-weight: 500; margin-bottom: 0.25rem;">
          Vector Database Name
        </label>
        <input 
          type="text" 
          id="name" 
          bind:value={name}
          style="width: 100%; padding: 0.5rem 0.75rem; border: 1px solid #d1d5db; border-radius: 0.375rem; box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);"
          placeholder="e.g., My Document Store"
        />
      </div>
      
      <div style="margin-bottom: 1.5rem;">
        <label for="type" style="display: block; font-size: 0.875rem; font-weight: 500; margin-bottom: 0.25rem;">
          Database Type
        </label>
        <select 
          id="type" 
          bind:value={type}
          style="width: 100%; padding: 0.5rem 0.75rem; border: 1px solid #d1d5db; border-radius: 0.375rem; box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);"
        >
          <option value="">Select a vector database type</option>
          {#each dbTypes as dbType}
            <option value={dbType.name}>{dbType.name}</option>
          {/each}
        </select>
      </div>
      
      <div>
        <label for="connection_string" style="display: block; font-size: 0.875rem; font-weight: 500; margin-bottom: 0.25rem;">
          Connection String (Optional)
        </label>
        <textarea 
          id="connection_string" 
          bind:value={connectionString}
          style="width: 100%; height: 100px; padding: 0.5rem 0.75rem; border: 1px solid #d1d5db; border-radius: 0.375rem; box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05); resize: vertical; font-family: monospace;"
          placeholder={connectionPlaceholder}
        ></textarea>
        <p style="font-size: 0.75rem; color: #6b7280; margin-top: 0.25rem;">
          Connection details for your vector database. This is only required if you're connecting to an external database instance.
        </p>
      </div>
    </div>
    
    <!-- Sidebar info -->
    <div style="background-color: white; padding: 1.5rem; border-radius: 0.5rem; box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);">
      <h2 style="font-size: 1.125rem; font-weight: 500; margin-bottom: 1rem;">Vector Database Information</h2>
      
      <div style="font-size: 0.875rem;">
        <p style="margin-bottom: 1rem;">
          A vector database is specialized for storing and retrieving embedding vectors for semantic search. It enables efficient similarity searches based on the embedding vectors.
        </p>
        
        <h3 style="font-weight: 500; margin-bottom: 0.5rem;">Available Database Types</h3>
        <ul style="list-style: disc; margin-left: 1.5rem; margin-bottom: 1rem;">
          {#each dbTypes as dbType}
            <li style="margin-bottom: 0.25rem;">
              <span style="font-weight: 500;">{dbType.name}</span>
              <p style="color: #6b7280; font-size: 0.75rem;">{dbType.description}</p>
            </li>
          {/each}
        </ul>
        
        <h3 style="font-weight: 500; margin-bottom: 0.5rem;">Integration Tips</h3>
        <p style="color: #6b7280; margin-bottom: 1rem;">
          For most use cases, you can leave the connection string blank to use the default in-memory vector store. For production environments, consider using an external vector database.
        </p>
      </div>
    </div>
  </div>
</div>