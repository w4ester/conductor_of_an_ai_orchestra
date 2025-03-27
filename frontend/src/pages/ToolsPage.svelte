<script lang="ts">
  import { onMount } from 'svelte';
  import { api } from '../lib/api';
  import { toolsStore } from '../lib/store';
  
  // State
  let loading = true;
  let error = '';
  let filterLanguage = 'all';
  let searchTerm = '';
  
  // Filtered and searched tools
  $: filteredTools = $toolsStore
    .filter(tool => filterLanguage === 'all' || tool.language === filterLanguage)
    .filter(tool => {
      if (!searchTerm) return true;
      const term = searchTerm.toLowerCase();
      return (
        tool.name.toLowerCase().includes(term) ||
        tool.description.toLowerCase().includes(term)
      );
    });
  
  // Load tools
  onMount(async () => {
    try {
      const tools = await api.getTools();
      toolsStore.set(tools);
    } catch (err) {
      console.error('Failed to load tools:', err);
      error = 'Failed to load tools. Please try again.';
    } finally {
      loading = false;
    }
  });
  
  // Delete tool
  async function deleteTool(id: string, name: string) {
    if (!confirm(`Are you sure you want to delete the tool "${name}"? This cannot be undone.`)) {
      return;
    }
    
    try {
      await api.deleteTool(id);
      
      // Update store by removing the deleted tool
      toolsStore.update(tools => tools.filter(tool => tool.id !== id));
    } catch (err) {
      console.error('Failed to delete tool:', err);
      error = `Failed to delete tool: ${err.message}`;
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
  
  // Get language color
  function getLanguageColor(language) {
    switch (language.toLowerCase()) {
      case 'python':
        return { bg: '#dbeafe', text: '#1e40af' }; // Blue
      case 'javascript':
        return { bg: '#fef3c7', text: '#92400e' }; // Yellow
      default:
        return { bg: '#f3f4f6', text: '#4b5563' }; // Gray
    }
  }
</script>

<div style="padding: 1.5rem;">
  <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem;">
    <h1 style="font-size: 1.5rem; font-weight: bold;">Tools</h1>
    <a href="#/tools/create" style="background-color: #2563eb; color: white; padding: 0.5rem 1rem; border-radius: 0.25rem; font-size: 0.875rem; text-decoration: none; display: flex; align-items: center;">
      <span style="margin-right: 0.25rem;">+</span> Create Tool
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
          placeholder="Search tools..." 
          style="width: 100%; padding: 0.5rem 0.75rem; border: 1px solid #d1d5db; border-radius: 0.375rem; box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);"
        />
      </div>
      <div>
        <select
          bind:value={filterLanguage}
          style="padding: 0.5rem 0.75rem; border: 1px solid #d1d5db; border-radius: 0.375rem; box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);"
        >
          <option value="all">All Languages</option>
          <option value="python">Python</option>
          <option value="javascript">JavaScript</option>
        </select>
      </div>
    </div>
  </div>
  
  <!-- Tools Grid -->
  {#if loading}
    <div style="display: flex; justify-content: center; padding: 2rem;">
      <p>Loading tools...</p>
    </div>
  {:else if filteredTools.length === 0}
    <div style="background-color: white; padding: 2rem; text-align: center; border-radius: 0.5rem; box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);">
      <p style="color: #6b7280;">No tools found matching your filters.</p>
      <a href="#/tools/create" style="display: inline-block; margin-top: 1rem; background-color: #2563eb; color: white; padding: 0.5rem 1rem; border-radius: 0.25rem; font-size: 0.875rem; text-decoration: none;">
        Create your first tool
      </a>
    </div>
  {:else}
    <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 1rem;">
      {#each filteredTools as tool}
        {@const langColor = getLanguageColor(tool.language)}
        <div style="background-color: white; padding: 1.5rem; border-radius: 0.5rem; box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06); display: flex; flex-direction: column;">
          <div style="display: flex; justify-content: space-between; margin-bottom: 0.75rem;">
            <h2 style="font-size: 1.125rem; font-weight: 500;">{tool.name}</h2>
            <span style={`background-color: ${langColor.bg}; color: ${langColor.text}; font-size: 0.75rem; padding: 0.125rem 0.5rem; border-radius: 9999px;`}>
              {tool.language}
            </span>
          </div>
          
          <p style="font-size: 0.875rem; color: #6b7280; margin-bottom: 1rem; flex-grow: 1;">
            {tool.description}
          </p>
          
          <div style="margin-bottom: 1rem; font-size: 0.75rem; color: #6b7280;">
            <p>Created: {formatDate(tool.created_at)}</p>
            {#if tool.updated_at && tool.updated_at !== tool.created_at}
              <p>Updated: {formatDate(tool.updated_at)}</p>
            {/if}
          </div>
          
          <div style="display: flex; gap: 0.5rem;">
            <a 
              href="#/tools/edit/{tool.id}" 
              style="flex: 1; text-align: center; padding: 0.375rem 0; font-size: 0.875rem; background-color: #eff6ff; color: #2563eb; border-radius: 0.25rem; text-decoration: none;"
            >
              Edit
            </a>
            <button 
              on:click={() => deleteTool(tool.id, tool.name)}
              style="flex: 1; text-align: center; padding: 0.375rem 0; font-size: 0.875rem; background-color: #fee2e2; color: #b91c1c; border-radius: 0.25rem; border: none; cursor: pointer;"
            >
              Delete
            </button>
          </div>
        </div>
      {/each}
    </div>
  {/if}
  
  <!-- Tools Information -->
  <div style="margin-top: 2rem; background-color: white; padding: 1.5rem; border-radius: 0.5rem; box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);">
    <h2 style="font-size: 1.25rem; font-weight: 500; margin-bottom: 1rem;">About Tools</h2>
    
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1.5rem;">
      <div>
        <h3 style="font-size: 1rem; font-weight: 500; margin-bottom: 0.5rem;">What are tools?</h3>
        <p style="font-size: 0.875rem; color: #4b5563;">
          Tools are functional components that extend the capabilities of language models. They allow models to perform specific tasks, access external data, or interact with other systems.
        </p>
      </div>
      
      <div>
        <h3 style="font-size: 1rem; font-weight: 500; margin-bottom: 0.5rem;">How to use tools</h3>
        <p style="font-size: 0.875rem; color: #4b5563;">
          When integrated with Ollama, tools can be called by the model during generation. The model can determine when to use tools based on the user's query and the context of the conversation.
        </p>
      </div>
      
      <div>
        <h3 style="font-size: 1rem; font-weight: 500; margin-bottom: 0.5rem;">Creating effective tools</h3>
        <p style="font-size: 0.875rem; color: #4b5563;">
          Focus on specific functionality, provide clear documentation, handle errors gracefully, and ensure your tool returns structured data that can be easily interpreted by the language model.
        </p>
      </div>
    </div>
  </div>
</div>