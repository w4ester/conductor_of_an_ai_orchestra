<script lang="ts">
  import { onMount } from 'svelte';
  import { api } from '../lib/api';
  import { documentsStore } from '../lib/store';
  
  // State
  let loading = true;
  let error = '';
  let searchTerm = '';
  let fileTypeFilter = 'all';
  
  // Load documents
  onMount(async () => {
    try {
      const documents = await api.getDocuments();
      documentsStore.set(documents);
      loading = false;
    } catch (err) {
      console.error('Failed to load documents:', err);
      error = 'Failed to load documents. Please try again.';
      loading = false;
    }
  });
  
  // Get unique file types
  $: fileTypes = ['all', ...new Set($documentsStore.map(doc => doc.file_type))];
  
  // Filtered and searched documents
  $: filteredDocuments = $documentsStore
    .filter(doc => fileTypeFilter === 'all' || doc.file_type === fileTypeFilter)
    .filter(doc => {
      if (!searchTerm) return true;
      const term = searchTerm.toLowerCase();
      return doc.title.toLowerCase().includes(term);
    });
  
  // Delete document
  async function deleteDocument(id: string, title: string) {
    if (!confirm(`Are you sure you want to delete the document "${title}"? This cannot be undone.`)) {
      return;
    }
    
    try {
      await api.deleteDocument(id);
      
      // Update store by removing the deleted document
      documentsStore.update(docs => docs.filter(doc => doc.id !== id));
    } catch (err) {
      console.error('Failed to delete document:', err);
      error = `Failed to delete document: ${err.message}`;
    }
  }
  
  // Extract text from document
  async function extractText(id: string) {
    try {
      const result = await api.extractDocumentText(id);
      console.log('Extracted text:', result.text);
      // In a real app, you might display this text or use it for RAG
      alert(`Text extracted successfully from document.\n\nPreview:\n${result.text.substring(0, 100)}...`);
    } catch (err) {
      console.error('Failed to extract text:', err);
      error = `Failed to extract text: ${err.message}`;
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
  
  // Get file icon based on extension
  function getFileIcon(fileType: string) {
    switch (fileType.toLowerCase()) {
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
    <h1 style="font-size: 1.5rem; font-weight: bold;">Documents</h1>
    <a href="#/documents/upload" style="background-color: #2563eb; color: white; padding: 0.5rem 1rem; border-radius: 0.25rem; font-size: 0.875rem; text-decoration: none; display: flex; align-items: center;">
      <span style="margin-right: 0.25rem;">+</span> Upload Document
    </a>
  </div>
  
  {#if error}
    <div style="background-color: #fee2e2; border: 1px solid #f87171; color: #b91c1c; padding: 0.75rem 1rem; border-radius: 0.25rem; margin-bottom: 1rem;" role="alert">
      <span>{error}</span>
    </div>
  {/if}
  
  <!-- Search and filters -->
  <div style="background-color: white; padding: 1rem; border-radius: 0.5rem; box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06); margin-bottom: 1.5rem;">
    <div style="display: flex; gap: 1rem; flex-wrap: wrap;">
      <div style="flex: 1;">
        <input 
          type="text" 
          bind:value={searchTerm}
          placeholder="Search documents..." 
          style="width: 100%; padding: 0.5rem 0.75rem; border: 1px solid #d1d5db; border-radius: 0.375rem; box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);"
        />
      </div>
      <div>
        <select
          bind:value={fileTypeFilter}
          style="padding: 0.5rem 0.75rem; border: 1px solid #d1d5db; border-radius: 0.375rem; box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);"
        >
          <option value="all">All File Types</option>
          {#each fileTypes.filter(type => type !== 'all') as fileType}
            <option value={fileType}>{fileType.toUpperCase()}</option>
          {/each}
        </select>
      </div>
    </div>
  </div>
  
  <!-- Documents Table -->
  {#if loading}
    <div style="display: flex; justify-content: center; padding: 2rem;">
      <p>Loading documents...</p>
    </div>
  {:else if filteredDocuments.length === 0}
    <div style="background-color: white; padding: 2rem; text-align: center; border-radius: 0.5rem; box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);">
      <p style="color: #6b7280;">No documents found matching your filters.</p>
      <a href="#/documents/upload" style="display: inline-block; margin-top: 1rem; background-color: #2563eb; color: white; padding: 0.5rem 1rem; border-radius: 0.25rem; font-size: 0.875rem; text-decoration: none;">
        Upload your first document
      </a>
    </div>
  {:else}
    <div style="background-color: white; border-radius: 0.5rem; box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06); overflow: hidden; overflow-x: auto;">
      <table style="min-width: 100%; border-collapse: collapse;">
        <thead>
          <tr style="border-bottom: 1px solid #e5e7eb; background-color: #f9fafb;">
            <th style="padding: 0.75rem 1.5rem; text-align: left; font-size: 0.875rem; font-weight: 500; color: #4b5563;">Document</th>
            <th style="padding: 0.75rem 1.5rem; text-align: left; font-size: 0.875rem; font-weight: 500; color: #4b5563;">Type</th>
            <th style="padding: 0.75rem 1.5rem; text-align: left; font-size: 0.875rem; font-weight: 500; color: #4b5563;">Uploaded</th>
            <th style="padding: 0.75rem 1.5rem; text-align: right; font-size: 0.875rem; font-weight: 500; color: #4b5563;">Actions</th>
          </tr>
        </thead>
        <tbody>
          {#each filteredDocuments as document}
            <tr style="border-bottom: 1px solid #e5e7eb;">
              <td style="padding: 1rem 1.5rem;">
                <div style="display: flex; align-items: center;">
                  <div style="font-size: 1.5rem; margin-right: 0.75rem;">{getFileIcon(document.file_type)}</div>
                  <div>
                    <p style="font-weight: 500;">{document.title}</p>
                  </div>
                </div>
              </td>
              <td style="padding: 1rem 1.5rem;">
                <span style="background-color: #f3f4f6; padding: 0.25rem 0.5rem; border-radius: 0.25rem; font-size: 0.75rem; text-transform: uppercase;">
                  {document.file_type}
                </span>
              </td>
              <td style="padding: 1rem 1.5rem; color: #6b7280; font-size: 0.875rem;">
                {formatDate(document.created_at)}
              </td>
              <td style="padding: 1rem 1.5rem; text-align: right;">
                <div style="display: flex; gap: 0.5rem; justify-content: flex-end;">
                  <button 
                    on:click={() => extractText(document.id)}
                    style="padding: 0.375rem 0.5rem; font-size: 0.75rem; background-color: #e0f2fe; color: #0369a1; border-radius: 0.25rem; border: none;"
                  >
                    Extract Text
                  </button>
                  <button 
                    on:click={() => deleteDocument(document.id, document.title)}
                    style="padding: 0.375rem 0.5rem; font-size: 0.75rem; background-color: #fee2e2; color: #b91c1c; border-radius: 0.25rem; border: none;"
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
  {/if}
  
  <!-- RAG Integration Info -->
  <div style="margin-top: 2rem; background-color: white; padding: 1.5rem; border-radius: 0.5rem; box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);">
    <h2 style="font-size: 1.25rem; font-weight: 500; margin-bottom: 1rem;">Using Documents with RAG</h2>
    
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1.5rem;">
      <div>
        <h3 style="font-size: 1rem; font-weight: 500; margin-bottom: 0.5rem;">Document Processing</h3>
        <p style="font-size: 0.875rem; color: #4b5563;">
          Uploaded documents are processed to extract text and create embeddings that can be used for semantic search in RAG systems.
        </p>
      </div>
      
      <div>
        <h3 style="font-size: 1rem; font-weight: 500; margin-bottom: 0.5rem;">RAG Integration</h3>
        <p style="font-size: 0.875rem; color: #4b5563;">
          After uploading documents, you can add them to existing RAG systems or create new ones. Documents will be automatically chunked and embedded.
        </p>
      </div>
      
      <div>
        <h3 style="font-size: 1rem; font-weight: 500; margin-bottom: 0.5rem;">Best Practices</h3>
        <p style="font-size: 0.875rem; color: #4b5563;">
          Use descriptive titles, ensure documents are text-extractable, and consider breaking large documents into smaller, more focused files for better retrieval.
        </p>
      </div>
    </div>
    
    <div style="margin-top: 1.5rem; text-align: center;">
      <a href="#/rag" style="display: inline-block; padding: 0.5rem 1rem; background-color: #eff6ff; color: #1e40af; border-radius: 0.25rem; font-size: 0.875rem; text-decoration: none;">
        Go to RAG Systems
      </a>
    </div>
  </div>
</div>