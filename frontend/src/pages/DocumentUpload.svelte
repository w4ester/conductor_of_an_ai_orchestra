<script lang="ts">
  import { onMount } from 'svelte';
  import { api } from '../lib/api';
  import { documentsStore } from '../lib/store';
  
  // State
  let title = '';
  let file: File | null = null;
  let uploadProgress = 0;
  let isUploading = false;
  let error = '';
  let success = '';
  
  // File input reference
  let fileInput: HTMLInputElement;
  
  // Handle file selection
  function handleFileSelect(event) {
    const files = event.target.files;
    if (files.length > 0) {
      file = files[0];
      // Default title to filename without extension
      if (!title) {
        title = file.name.split('.').slice(0, -1).join('.');
      }
    }
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
  
  // Get file size in readable format
  function getFileSize(size: number) {
    if (size < 1024) {
      return `${size} B`;
    } else if (size < 1024 * 1024) {
      return `${(size / 1024).toFixed(1)} KB`;
    } else {
      return `${(size / (1024 * 1024)).toFixed(1)} MB`;
    }
  }
  
  // Upload document
  async function uploadDocument() {
    if (!file) {
      error = 'Please select a file to upload';
      return;
    }
    
    if (!title.trim()) {
      error = 'Please enter a title for the document';
      return;
    }
    
    try {
      isUploading = true;
      error = '';
      success = '';
      uploadProgress = 10; // Start progress
      
      // Upload file
      const document = await api.uploadDocument(file, title);
      
      uploadProgress = 90; // Almost done
      
      // Update documents store
      const documents = await api.getDocuments();
      documentsStore.set(documents);
      
      uploadProgress = 100; // Complete
      success = `Document "${title}" has been uploaded successfully`;
      
      // Reset form
      title = '';
      file = null;
      if (fileInput) {
        fileInput.value = '';
      }
    } catch (err) {
      console.error('Failed to upload document:', err);
      error = `Failed to upload document: ${err.message}`;
    } finally {
      isUploading = false;
      // Reset progress after a delay
      setTimeout(() => {
        uploadProgress = 0;
      }, 3000);
    }
  }
  
  // Load documents on mount
  onMount(async () => {
    try {
      const documents = await api.getDocuments();
      documentsStore.set(documents);
    } catch (err) {
      console.error('Failed to load documents:', err);
    }
  });
  
  // Cancel upload
  function cancel() {
    window.history.back();
  }
</script>

<div style="padding: 1.5rem;">
  <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem;">
    <h1 style="font-size: 1.5rem; font-weight: bold;">Upload Document</h1>
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
    <!-- Upload Form -->
    <div style="background-color: white; padding: 1.5rem; border-radius: 0.5rem; box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);">
      <h2 style="font-size: 1.125rem; font-weight: 500; margin-bottom: 1rem;">Document Details</h2>
      
      <div style="margin-bottom: 1.5rem;">
        <label for="title" style="display: block; font-size: 0.875rem; font-weight: 500; margin-bottom: 0.25rem;">
          Document Title
        </label>
        <input 
          type="text" 
          id="title" 
          bind:value={title}
          style="width: 100%; padding: 0.5rem 0.75rem; border: 1px solid #d1d5db; border-radius: 0.375rem; box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);"
          placeholder="Enter a descriptive title for the document"
        />
      </div>
      
      <div style="margin-bottom: 1.5rem;">
        <label for="file" style="display: block; font-size: 0.875rem; font-weight: 500; margin-bottom: 0.25rem;">
          File Upload
        </label>
        <div 
          style="border: 2px dashed #d1d5db; padding: 2rem; border-radius: 0.375rem; display: flex; flex-direction: column; align-items: center; justify-content: center; cursor: pointer;"
          on:click={() => fileInput.click()}
        >
          <input 
            type="file" 
            id="file" 
            bind:this={fileInput}
            on:change={handleFileSelect}
            style="display: none;"
            accept=".pdf,.docx,.doc,.txt,.md,.csv"
          />
          <div style="font-size: 2rem; margin-bottom: 0.5rem;">📄</div>
          <p style="margin-bottom: 0.5rem; font-size: 0.875rem; font-weight: 500;">
            {file ? file.name : 'Drag and drop file here or click to upload'}
          </p>
          <p style="font-size: 0.75rem; color: #6b7280;">
            {file 
              ? `${getFileSize(file.size)} - ${file.type}` 
              : 'Supported formats: PDF, DOCX, TXT, MD, CSV'}
          </p>
        </div>
      </div>
      
      {#if uploadProgress > 0}
        <div style="margin-bottom: 1.5rem;">
          <div style="width: 100%; background-color: #e5e7eb; height: 0.5rem; border-radius: 9999px; overflow: hidden;">
            <div 
              style={`width: ${uploadProgress}%; background-color: #2563eb; height: 100%; transition: width 0.3s ease;`}
            ></div>
          </div>
          <p style="font-size: 0.75rem; color: #6b7280; margin-top: 0.25rem; text-align: center;">
            {uploadProgress === 100 ? 'Upload complete!' : 'Uploading...'}
          </p>
        </div>
      {/if}
      
      <div>
        <button 
          on:click={uploadDocument}
          disabled={isUploading}
          style="width: 100%; padding: 0.5rem 1rem; border-radius: 0.25rem; background-color: #2563eb; color: white; opacity: ${isUploading ? '0.7' : '1'};"
        >
          {isUploading ? 'Uploading...' : 'Upload Document'}
        </button>
      </div>
    </div>
    
    <!-- Info Section -->
    <div>
      <div style="background-color: white; padding: 1.5rem; border-radius: 0.5rem; box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06); margin-bottom: 1.5rem;">
        <h2 style="font-size: 1.125rem; font-weight: 500; margin-bottom: 1rem;">Document Processing</h2>
        <p style="font-size: 0.875rem; color: #4b5563; margin-bottom: 1rem;">
          Uploaded documents will be processed automatically for use in RAG systems. The text is extracted and embeddings are created for semantic search.
        </p>
        
        <div style="border-left: 4px solid #e5e7eb; padding-left: 1rem; margin-bottom: 1rem;">
          <h3 style="font-size: 0.875rem; font-weight: 500; margin-bottom: 0.25rem;">Supported File Types</h3>
          <ul style="list-style: disc; margin-left: 1.5rem; font-size: 0.875rem; color: #4b5563;">
            <li>PDF Documents (.pdf)</li>
            <li>Word Documents (.docx, .doc)</li>
            <li>Text Files (.txt)</li>
            <li>Markdown Files (.md)</li>
            <li>CSV Files (.csv)</li>
          </ul>
        </div>
        
        <div style="font-size: 0.875rem; color: #4b5563;">
          <p>Documents are stored securely and can be managed from the Documents page.</p>
        </div>
      </div>
      
      <div style="background-color: white; padding: 1.5rem; border-radius: 0.5rem; box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);">
        <h2 style="font-size: 1.125rem; font-weight: 500; margin-bottom: 1rem;">RAG Document Tips</h2>
        <ul style="list-style: disc; margin-left: 1.5rem; font-size: 0.875rem; color: #4b5563;">
          <li>Use descriptive titles that help identify the document's content</li>
          <li>For best results, ensure PDFs have proper text encoding (not just scanned images)</li>
          <li>Consider chunking large documents into smaller segments for better retrieval</li>
          <li>Documents will be automatically analyzed and processed for semantic search</li>
          <li>Add documents to RAG systems from the Documents management page</li>
        </ul>
      </div>
    </div>
  </div>
</div>