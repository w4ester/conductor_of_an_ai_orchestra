<script lang="ts">
  import { onMount } from 'svelte';
  import { api } from '../lib/api';
  import { promptsStore } from '../lib/store';
  import type { Prompt } from '../lib/api';
  
  // State
  let loading = true;
  let error = '';
  let prompts: Prompt[] = [];
  let totalPrompts = 0;
  let currentPage = 0;
  let pageSize = 10;
  
  // Categories for filtering
  const categories = ['All', 'General', 'Coding', 'Research', 'Creative', 'Education', 'Business'];
  let selectedCategory = 'All';
  
  // Filtered prompts
  $: filteredCategory = selectedCategory === 'All' ? undefined : selectedCategory;
  
  // Load prompts with filtering and pagination
  async function loadPrompts() {
    loading = true;
    error = '';
    
    try {
      const response = await api.getPrompts(currentPage, pageSize, filteredCategory);
      prompts = response.items;
      totalPrompts = response.total;
      promptsStore.set(prompts);
    } catch (err) {
      console.error('Failed to load prompts:', err);
      error = `Failed to load prompts: ${err.message}`;
    } finally {
      loading = false;
    }
  }
  
  // When category or page changes, reload prompts
  $: {
    if (selectedCategory !== undefined) {
      currentPage = 0; // Reset to first page when changing category
      loadPrompts();
    }
  }
  
  // Calculate total pages
  $: totalPages = Math.ceil(totalPrompts / pageSize);
  
  // Page navigation
  function nextPage() {
    if (currentPage < totalPages - 1) {
      currentPage++;
      loadPrompts();
    }
  }
  
  function prevPage() {
    if (currentPage > 0) {
      currentPage--;
      loadPrompts();
    }
  }
  
  // Initial load
  onMount(() => {
    loadPrompts();
  });
  
  // Delete prompt
  async function deletePrompt(id: string, title: string) {
    if (!confirm(`Are you sure you want to delete the prompt "${title}"? This cannot be undone.`)) {
      return;
    }
    
    try {
      await api.deletePrompt(id);
      
      // Reload prompts after deletion
      loadPrompts();
    } catch (err) {
      console.error('Failed to delete prompt:', err);
      error = `Failed to delete prompt: ${err.message}`;
    }
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
</script>

<div style="padding: 1.5rem;">
  <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem;">
    <h1 style="font-size: 1.5rem; font-weight: bold;">Prompts</h1>
    <a href="#/prompts/create" style="background-color: #2563eb; color: white; padding: 0.5rem 1rem; border-radius: 0.25rem; font-size: 0.875rem; text-decoration: none; display: flex; align-items: center;">
      <span style="margin-right: 0.25rem;">+</span> Create Prompt
    </a>
  </div>
  
  {#if error}
    <div style="background-color: #fee2e2; border: 1px solid #f87171; color: #b91c1c; padding: 0.75rem 1rem; border-radius: 0.25rem; margin-bottom: 1rem;" role="alert">
      <span>{error}</span>
    </div>
  {/if}
  
  <!-- Filtering controls -->
  <div style="background-color: white; padding: 1rem; border-radius: 0.5rem; box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06); margin-bottom: 1.5rem;">
    <div style="display: flex; gap: 0.5rem; flex-wrap: wrap;">
      {#each categories as category}
        <button
          on:click={() => selectedCategory = category}
          style="padding: 0.25rem 0.75rem; border-radius: 0.25rem; font-size: 0.875rem; ${selectedCategory === category ? 'background-color: #2563eb; color: white;' : 'background-color: #f3f4f6; color: #4b5563;'}"
        >
          {category}
        </button>
      {/each}
    </div>
  </div>
  
  <!-- Prompts Grid -->
  {#if loading}
    <div style="display: flex; justify-content: center; padding: 2rem;">
      <p>Loading prompts...</p>
    </div>
  {:else if prompts.length === 0}
    <div style="background-color: white; padding: 2rem; text-align: center; border-radius: 0.5rem; box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);">
      <p style="color: #6b7280;">No prompts found in this category.</p>
      <a href="#/prompts/create" style="display: inline-block; margin-top: 1rem; background-color: #2563eb; color: white; padding: 0.5rem 1rem; border-radius: 0.25rem; font-size: 0.875rem; text-decoration: none;">
        Create your first prompt
      </a>
    </div>
  {:else}
    <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 1rem;">
      {#each prompts as prompt}
        <div style="background-color: white; padding: 1.5rem; border-radius: 0.5rem; box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);">
          <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 0.75rem;">
            <h2 style="font-size: 1.125rem; font-weight: 500;">{prompt.title}</h2>
            {#if prompt.category}
              <span style="background-color: #e0f2fe; color: #0369a1; font-size: 0.75rem; padding: 0.125rem 0.5rem; border-radius: 9999px;">
                {prompt.category}
              </span>
            {/if}
          </div>
          
          <p style="font-size: 0.875rem; color: #6b7280; display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden;">
            {prompt.content}
          </p>
          
          <div style="margin-top: 0.75rem; font-size: 0.75rem; color: #6b7280;">
            <p>Model: {prompt.model}</p>
            <p>Created: {formatDate(prompt.created_at)}</p>
          </div>
          
          {#if prompt.tags && prompt.tags.length > 0}
            <div style="display: flex; flex-wrap: wrap; gap: 0.25rem; margin-top: 0.75rem;">
              {#each prompt.tags as tag}
                <span style="background-color: #f3f4f6; font-size: 0.75rem; padding: 0.125rem 0.5rem; border-radius: 9999px;">
                  {tag}
                </span>
              {/each}
            </div>
          {/if}
          
          <div style="display: flex; gap: 0.5rem; margin-top: 1rem;">
            <a 
              href="#/prompts/edit/{prompt.id}" 
              style="flex: 1; text-align: center; padding: 0.375rem 0; font-size: 0.875rem; background-color: #eff6ff; color: #2563eb; border-radius: 0.25rem; text-decoration: none;"
            >
              Edit
            </a>
            <button 
              on:click={() => deletePrompt(prompt.id, prompt.title)}
              style="flex: 1; text-align: center; padding: 0.375rem 0; font-size: 0.875rem; background-color: #fee2e2; color: #b91c1c; border-radius: 0.25rem; border: none; cursor: pointer;"
            >
              Delete
            </button>
          </div>
        </div>
      {/each}
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
