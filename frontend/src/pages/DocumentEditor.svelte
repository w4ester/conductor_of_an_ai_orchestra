<script lang="ts">
  import { onMount } from 'svelte';
  import { api } from '../lib/api';
  import { documentsStore } from '../lib/store';
  
  // Props
  export let isEdit = false;
  export let documentId = '';
  export let readOnly = false;
  
  // State
  let document = {
    title: '',
    content: '',
    file_type: 'text'
  };
  let loading = false;
  let saving = false;
  let error = '';
  let success = '';
  
  // File type options
  const fileTypes = ['text', 'markdown', 'html', 'json'];
  
  // Load document if editing
  onMount(async () => {
    if (isEdit && documentId) {
      loading = true;
      try {
        const doc = await api.getDocument(documentId);
        document = {
          title: doc.title || '',
          content: doc.content || '',
          file_type: doc.file_type || 'text'
        };
      } catch (err) {
        console.error('Failed to load document:', err);
        error = `Failed to load document: ${err.message}`;
      } finally {
        loading = false;
      }
    }
  });
  
  // Save document
  async function saveDocument() {
    if (!document.title.trim()) {
      error = 'Document title is required';
      return;
    }
    
    saving = true;
    error = '';
    success = '';
    
    try {
      if (isEdit && documentId) {
        // Update existing document
        await api.updateDocument(documentId, document);
        success = 'Document updated successfully';
      } else {
        // Create new document
        const result = await api.createDocument(document);
        success = 'Document created successfully';
        // Redirect to edit page after creation
        setTimeout(() => {
          window.location.hash = `#/documents/edit/${result.id}`;
        }, 1500);
      }
      
      // Refresh documents store
      const response = await api.getDocuments();
      documentsStore.set(response.items);
    } catch (err) {
      console.error('Failed to save document:', err);
      error = `Failed to save document: ${err.message}`;
    } finally {
      saving = false;
    }
  }
  
  // Cancel editing
  function cancel() {
    window.location.hash = '#/documents';
  }
</script>

<div class="page-container">
  <div class="page-header">
    <h1 class="page-title">
      {#if readOnly}
        View Document
      {:else}
        {isEdit ? 'Edit' : 'Create'} Document
      {/if}
    </h1>
    <div class="action-buttons">
      <button class="btn btn-cancel" on:click={cancel}>
        Cancel
      </button>
      {#if !readOnly}
        <button 
          class="btn btn-save" 
          on:click={saveDocument} 
          disabled={saving}
        >
          {#if saving}
            <span class="loading-spinner"></span>
            Saving...
          {:else}
            {isEdit ? 'Update' : 'Create'} Document
          {/if}
        </button>
      {/if}
    </div>
  </div>
  
  {#if loading}
    <div class="loading-container">
      <div class="loading-spinner large"></div>
      <p>Loading document...</p>
    </div>
  {:else}
    {#if error}
      <div class="error-alert">
        <span>{error}</span>
        <button class="close-button" on:click={() => error = ''}>×</button>
      </div>
    {/if}
    
    {#if success}
      <div class="success-alert">
        <span>{success}</span>
        <button class="close-button" on:click={() => success = ''}>×</button>
      </div>
    {/if}
    
    <div class="editor-form">
      <div class="form-group">
        <label for="title">Document Title</label>
        <input 
          type="text" 
          id="title" 
          bind:value={document.title} 
          placeholder="Enter document title" 
          class="form-input"
          readonly={readOnly}
        />
      </div>
      
      <div class="form-group">
        <label for="file-type">Document Type</label>
        <select id="file-type" bind:value={document.file_type} class="form-select" disabled={readOnly}>
          {#each fileTypes as type}
            <option value={type}>{type.toUpperCase()}</option>
          {/each}
        </select>
      </div>
      
      <div class="form-group">
        <label for="content">Document Content</label>
        <textarea 
          id="content" 
          bind:value={document.content} 
          placeholder="Enter document content" 
          class="form-textarea"
          rows="20"
          readonly={readOnly}
        ></textarea>
      </div>
    </div>
  {/if}
</div>

<style>
  .page-container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 1.5rem;
  }
  
  .page-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 2rem;
    padding-bottom: 1rem;
    border-bottom: 1px solid #e5e7eb;
  }
  
  .page-title {
    font-size: 1.5rem;
    font-weight: 600;
    color: #111827;
    margin: 0;
  }
  
  .action-buttons {
    display: flex;
    gap: 0.75rem;
  }
  
  .btn {
    padding: 0.5rem 1rem;
    font-size: 0.875rem;
    font-weight: 500;
    border-radius: 0.375rem;
    cursor: pointer;
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    transition: all 0.2s;
  }
  
  .btn-cancel {
    background-color: white;
    color: #4b5563;
    border: 1px solid #d1d5db;
  }
  
  .btn-cancel:hover {
    background-color: #f9fafb;
  }
  
  .btn-save {
    background-color: #3b82f6;
    color: white;
    border: none;
  }
  
  .btn-save:hover:not(:disabled) {
    background-color: #2563eb;
  }
  
  .btn:disabled {
    opacity: 0.7;
    cursor: not-allowed;
  }
  
  .loading-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 4rem 0;
  }
  
  .loading-spinner {
    display: inline-block;
    width: 1rem;
    height: 1rem;
    border: 2px solid rgba(255, 255, 255, 0.3);
    border-radius: 50%;
    border-top-color: white;
    animation: spin 1s ease-in-out infinite;
  }
  
  .loading-spinner.large {
    width: 2.5rem;
    height: 2.5rem;
    border-width: 3px;
    border-color: rgba(59, 130, 246, 0.3);
    border-top-color: #3b82f6;
    margin-bottom: 1rem;
  }
  
  @keyframes spin {
    to { transform: rotate(360deg); }
  }
  
  .error-alert {
    background-color: #fee2e2;
    color: #b91c1c;
    padding: 1rem;
    border-radius: 0.375rem;
    margin-bottom: 1.5rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border: 1px solid #f87171;
  }
  
  .success-alert {
    background-color: #d1fae5;
    color: #065f46;
    padding: 1rem;
    border-radius: 0.375rem;
    margin-bottom: 1.5rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border: 1px solid #6ee7b7;
  }
  
  .close-button {
    background: none;
    border: none;
    font-size: 1.25rem;
    line-height: 1;
    cursor: pointer;
    color: inherit;
  }
  
  .editor-form {
    background-color: white;
    border-radius: 0.5rem;
    box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
    padding: 1.5rem;
  }
  
  .form-group {
    margin-bottom: 1.5rem;
  }
  
  .form-group label {
    display: block;
    font-size: 0.875rem;
    font-weight: 500;
    color: #374151;
    margin-bottom: 0.5rem;
  }
  
  .form-input,
  .form-select,
  .form-textarea {
    width: 100%;
    padding: 0.625rem 0.75rem;
    font-size: 0.875rem;
    border: 1px solid #d1d5db;
    border-radius: 0.375rem;
    outline: none;
    background-color: white;
    color: #111827;
    transition: border-color 0.2s, box-shadow 0.2s;
  }
  
  .form-input:focus,
  .form-select:focus,
  .form-textarea:focus {
    border-color: #3b82f6;
    box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.3);
  }
  
  .form-textarea {
    resize: vertical;
    min-height: 300px;
    line-height: 1.5;
    font-family: ui-monospace, SFMono-Regular, 'Courier New', monospace;
  }
</style>
