<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import { api } from '../lib/api';
  import { documentsStore } from '../lib/store';
  import type { Document } from '../lib/api';
  
  // State
  let loading = true;
  let error = '';
  let success = '';
  let documents: Document[] = [];
  let totalDocuments = 0;
  let currentPage = 0;
  let pageSize = 10;
  
  // Subscription
  let documentsUnsubscribe;
  
  // File types for filtering
  const fileTypes = ['All', 'Text', 'PDF', 'Markdown', 'Word', 'HTML', 'JSON'];
  let selectedFileType = 'All';
  
  // Filtered documents
  $: filteredFileType = selectedFileType === 'All' ? undefined : selectedFileType.toLowerCase();
  
  // Load documents with filtering and pagination
  async function loadDocuments() {
    loading = true;
    error = '';
    
    try {
      const response = await api.getDocuments(currentPage, pageSize, filteredFileType);
      documents = response.items;
      totalDocuments = response.total;
      documentsStore.set(documents);
    } catch (err) {
      console.error('Failed to load documents:', err);
      error = `Failed to load documents: ${err.message}`;
    } finally {
      loading = false;
    }
  }
  
  // When file type or page changes, reload documents
  $: {
    if (selectedFileType !== undefined) {
      currentPage = 0; // Reset to first page when changing filter
      loadDocuments();
    }
  }
  
  // Calculate total pages
  $: totalPages = Math.ceil(totalDocuments / pageSize);
  
  // Page navigation
  function nextPage() {
    if (currentPage < totalPages - 1) {
      currentPage++;
      loadDocuments();
    }
  }
  
  function prevPage() {
    if (currentPage > 0) {
      currentPage--;
      loadDocuments();
    }
  }
  
  // Format file size
  function formatFileSize(size: number): string {
    if (!size) return "Unknown size";
    
    const units = ['B', 'KB', 'MB', 'GB'];
    let formattedSize = size;
    let unitIndex = 0;
    
    while (formattedSize >= 1024 && unitIndex < units.length - 1) {
      formattedSize /= 1024;
      unitIndex++;
    }
    
    return `${formattedSize.toFixed(1)} ${units[unitIndex]}`;
  }
  
  // Format date
  function formatDate(dateString: string | undefined): string {
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
  
  // Delete document
  async function deleteDocument(id: string, title: string) {
    if (!confirm(`Are you sure you want to delete the document "${title}"? This cannot be undone.`)) {
      return;
    }
    
    try {
      // Make sure we're calling the correct endpoint
      await api.deleteDocument(id);
      
      // Update local state to remove the deleted document
      documents = documents.filter(doc => doc.id !== id);
      documentsStore.set(documents);
      
      // Show success message
      error = ''; // Clear any existing errors
      success = `Document "${title}" deleted successfully`;
      
      // We won't reload all documents as that's an extra API call
      // Just update our local state (already done above)
    } catch (err) {
      console.error('Failed to delete document:', err);
      error = `Failed to delete document: ${err.message}`;
    }
  }
  
  // Add this missing file upload handler
  async function handleFileUpload(event) {
    const file = event.target.files[0];
    if (!file) return;
    
    try {
      // Ask for document title
      const title = prompt("Enter a title for this document:", file.name.split('.')[0]);
      if (!title) return; // User cancelled
      
      loading = true;
      await api.uploadDocument(file, title);
      
      // Reset the file input
      event.target.value = '';
      
      // Reload documents to show the new one
      loadDocuments();
      
    } catch (err) {
      console.error('Failed to upload document:', err);
      error = `Failed to upload document: ${err.message}`;
      loading = false;
    }
  }
  
  // Initial load and store subscription
  onMount(() => {
    loadDocuments();
    
    // Subscribe to the documents store
    documentsUnsubscribe = documentsStore.subscribe(value => {
      if (value && value.length > 0) {
        documents = value;
      }
    });
  });
  
  // Clean up subscription
  onDestroy(() => {
    if (documentsUnsubscribe) {
      documentsUnsubscribe();
    }
  });
</script>

<div style="padding: 1.5rem;">
  <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem;">
    <h1 style="font-size: 1.5rem; font-weight: bold;">Documents</h1>
    <div style="display: flex; gap: 0.5rem;">
      <a href="#/documents/create" style="background-color: #2563eb; color: white; padding: 0.5rem 1rem; border-radius: 0.25rem; font-size: 0.875rem; text-decoration: none; display: flex; align-items: center;">
        <span style="margin-right: 0.25rem;">+</span> Create Document
      </a>
      <label for="file-upload" style="background-color: #4f46e5; color: white; padding: 0.5rem 1rem; border-radius: 0.25rem; font-size: 0.875rem; cursor: pointer; display: flex; align-items: center;">
        <span style="margin-right: 0.25rem;">↑</span> Upload File
      </label>
      <input id="file-upload" type="file" style="display: none;" on:change={handleFileUpload} />
    </div>
  </div>
  
  {#if error}
    <div style="background-color: #fee2e2; border: 1px solid #f87171; color: #b91c1c; padding: 0.75rem 1rem; border-radius: 0.25rem; margin-bottom: 1rem;" role="alert">
      <span>{error}</span>
    </div>
  {/if}
  
  {#if success}
    <div style="background-color: #d1fae5; border: 1px solid #6ee7b7; color: #065f46; padding: 0.75rem 1rem; border-radius: 0.25rem; margin-bottom: 1rem;" role="alert">
      <span>{success}</span>
      <button 
        style="float: right; background: none; border: none; font-size: 1.25rem; line-height: 1; cursor: pointer; color: inherit;"
        on:click={() => success = ''}
      >
        ×
      </button>
    </div>
  {/if}
  
  <!-- Filtering controls -->
  <div style="background-color: white; padding: 1rem; border-radius: 0.5rem; box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06); margin-bottom: 1.5rem;">
    <div style="display: flex; gap: 0.5rem; flex-wrap: wrap;">
      {#each fileTypes as fileType}
        <button
          on:click={() => selectedFileType = fileType}
          style="padding: 0.25rem 0.75rem; border-radius: 0.25rem; font-size: 0.875rem; ${selectedFileType === fileType ? 'background-color: #2563eb; color: white;' : 'background-color: #f3f4f6; color: #4b5563;'}"
        >
          {fileType}
        </button>
      {/each}
    </div>
  </div>
  
  <!-- Documents List -->
  {#if loading}
    <div style="display: flex; justify-content: center; padding: 2rem;">
      <p>Loading documents...</p>
    </div>
  {:else if documents.length === 0}
    <div style="background-color: white; padding: 2rem; text-align: center; border-radius: 0.5rem; box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);">
      <p style="color: #6b7280;">No documents found.</p>
      <div style="display: flex; justify-content: center; gap: 1rem; margin-top: 1rem;">
        <a href="#/documents/create" style="display: inline-block; background-color: #2563eb; color: white; padding: 0.5rem 1rem; border-radius: 0.25rem; font-size: 0.875rem; text-decoration: none;">
          Create a document
        </a>
        <label for="empty-file-upload" style="display: inline-block; background-color: #4f46e5; color: white; padding: 0.5rem 1rem; border-radius: 0.25rem; font-size: 0.875rem; cursor: pointer;">
          Upload a file
        </label>
        <input id="empty-file-upload" type="file" style="display: none;" on:change={handleFileUpload} />
      </div>
    </div>
  {:else}
    <div style="overflow-x: auto;">
      <table style="width: 100%; border-collapse: separate; border-spacing: 0; border-radius: 0.5rem; overflow: hidden; box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);">
        <thead>
          <tr style="background-color: #f9fafb;">
            <th style="padding: 0.75rem 1rem; text-align: left; font-weight: 500; color: #374151; border-bottom: 1px solid #e5e7eb;">Title</th>
            <th style="padding: 0.75rem 1rem; text-align: left; font-weight: 500; color: #374151; border-bottom: 1px solid #e5e7eb;">Type</th>
            <th style="padding: 0.75rem 1rem; text-align: left; font-weight: 500; color: #374151; border-bottom: 1px solid #e5e7eb;">Created</th>
            <th style="padding: 0.75rem 1rem; text-align: left; font-weight: 500; color: #374151; border-bottom: 1px solid #e5e7eb;">Actions</th>
          </tr>
        </thead>
        <tbody>
          {#each documents as document}
            <tr style="background-color: white; border-bottom: 1px solid #e5e7eb;">
              <td style="padding: 0.75rem 1rem; border-bottom: 1px solid #e5e7eb;">
                <div style="font-weight: 500;">{document.title}</div>
                <div style="font-size: 0.875rem; color: #6b7280; margin-top: 0.25rem;">
                  ID: {document.id}
                </div>
              </td>
              <td style="padding: 0.75rem 1rem; border-bottom: 1px solid #e5e7eb;">
                <span style="display: inline-block; padding: 0.25rem 0.5rem; background-color: #e0f2fe; color: #0369a1; border-radius: 9999px; font-size: 0.75rem; text-transform: uppercase;">
                  {document.file_type}
                </span>
              </td>
              <td style="padding: 0.75rem 1rem; border-bottom: 1px solid #e5e7eb;">
                {formatDate(document.created_at)}
              </td>
              <td style="padding: 0.75rem 1rem; border-bottom: 1px solid #e5e7eb;">
                <div style="display: flex; gap: 0.5rem;">
                  <a 
                    href={`#/documents/edit/${document.id}`} 
                    style="padding: 0.375rem 0.75rem; background-color: #eff6ff; color: #2563eb; border-radius: 0.25rem; font-size: 0.875rem; text-decoration: none;"
                  >
                    View
                  </a>
                  <a 
                    href={`#/documents/edit/${document.id}`} 
                    style="padding: 0.375rem 0.75rem; background-color: #f3f4f6; color: #1f2937; border-radius: 0.25rem; font-size: 0.875rem; text-decoration: none;"
                  >
                    Edit
                  </a>
                  <button 
                    on:click={() => deleteDocument(document.id, document.title)}
                    style="padding: 0.375rem 0.75rem; background-color: #fee2e2; color: #b91c1c; border: none; border-radius: 0.25rem; font-size: 0.875rem; cursor: pointer;"
                  >
                    Delete
                  </button>
                </div>
              </td>
            </tr>
          {/each}
        </tbody>
      </table>
    </div>
    
    <!-- Pagination controls -->
    {#if totalPages > 1}
      <div style="display: flex; justify-content: center; margin-top: 1.5rem; gap: 0.5rem;">
        <button 
          on:click={prevPage} 
          disabled={currentPage === 0}
          style="padding: 0.5rem 1rem; border: 1px solid #d1d5db; border-radius: 0.25rem; ${currentPage === 0 ? 'opacity: 0.5; cursor: not-allowed;' : 'cursor: pointer;'}"
        >
          Previous
        </button>
        
        <span style="padding: 0.5rem 1rem; background-color: #f3f4f6; border-radius: 0.25rem;">
          Page {currentPage + 1} of {totalPages}
        </span>
        
        <button 
          on:click={nextPage} 
          disabled={currentPage >= totalPages - 1}
          style="padding: 0.5rem 1rem; border: 1px solid #d1d5db; border-radius: 0.25rem; ${currentPage >= totalPages - 1 ? 'opacity: 0.5; cursor: not-allowed;' : 'cursor: pointer;'}"
        >
          Next
        </button>
      </div>
    {/if}
  {/if}
</div>