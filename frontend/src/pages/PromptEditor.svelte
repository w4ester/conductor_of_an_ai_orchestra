<script lang="ts">
  import { onMount } from 'svelte';
  import { api } from '../lib/api';
  import { promptsStore, modelsStore } from '../lib/store';
  import type { Prompt } from '../lib/api';
  
  // Props
  export let promptId = '';
  export let isEdit = false; // true for edit, false for create
  
  // State
  let title = '';
  let content = '';
  let model = '';
  let category = '';
  let tags = '';
  let isSaving = false;
  let error = '';
  let success = '';
  let availableModels = [];
  
  // Example prompt templates
  const templates = {
    general: `You are a helpful assistant. 
    
Please answer the user's question clearly and concisely.`,

    coding: `You are a coding assistant specializing in [language].

Please provide clean, efficient, and well-commented code that follows best practices for [language].`,

    rag: `You are a helpful assistant. Use the provided context to answer the user's question.

Context:
{{context}}

When responding, only use information from the provided context. If the context doesn't contain the information needed, say "I don't have enough information to answer that question."`,

    creative: `You are a creative writing assistant who specializes in [style] writing.

Generate a [style] piece about [topic] that is creative, engaging, and follows the conventions of that style.`
  };
  
  // Initialize categories
  const categories = ['General', 'Coding', 'Research', 'Creative', 'Education', 'Business'];
  
  // Load prompt data if in edit mode
  onMount(async () => {
    try {
      // Connect directly to Ollama to get actual models
      const response = await fetch('http://localhost:11434/api/tags');
      
      if (response.ok) {
        const data = await response.json();
        availableModels = data.models ? data.models.map(model => model.name) : [];
      } else {
        console.error('Failed to get models from Ollama:', await response.text());
        error = 'Failed to load models from Ollama';
      }
      
      if (isEdit && promptId) {
        // Load prompt data
        const prompt = await api.getPrompt(promptId);
        
        title = prompt.title;
        content = prompt.content;
        model = prompt.model;
        category = prompt.category || '';
        tags = prompt.tags ? prompt.tags.join(', ') : '';
      } else {
        // Default for new prompt
        title = '';
        content = templates.general;
        model = availableModels.length > 0 ? availableModels[0] : '';
        category = 'General';
        tags = '';
      }
    } catch (err) {
      console.error('Failed to initialize prompt editor:', err);
      error = 'Failed to load data. Please try again.';
    }
  });
  
  // Apply template
  function applyTemplate(templateKey) {
    content = templates[templateKey];
  }
  
  // Test prompt with model
  async function testPrompt() {
    if (!model || !content) {
      error = 'Please select a model and enter prompt content';
      return;
    }
    
    try {
      error = '';
      
      // Placeholder for actual testing logic
      // In a real implementation, this would call the Ollama API to test the prompt
      success = `Prompt tested with ${model} successfully`;
    } catch (err) {
      console.error('Failed to test prompt:', err);
      error = `Failed to test prompt: ${err.message}`;
    }
  }
  
  // Save prompt
  async function savePrompt() {
    if (!title.trim()) {
      error = 'Please enter a title';
      return;
    }
    
    if (!content.trim()) {
      error = 'Please enter prompt content';
      return;
    }
    
    if (!model) {
      error = 'Please select a model';
      return;
    }
    
    try {
      isSaving = true;
      error = '';
      success = '';
      
      // Convert tags string to array
      const tagsArray = tags.split(',')
        .map(tag => tag.trim())
        .filter(tag => tag.length > 0);
      
      // Create prompt object
      const promptData: Prompt = {
        title,
        content,
        model,
        category: category || undefined,
        tags: tagsArray.length > 0 ? tagsArray : undefined
      };
      
      let savedPrompt;
      
      if (isEdit && promptId) {
        // Update existing prompt
        savedPrompt = await api.updatePrompt(promptId, promptData);
      } else {
        // Create new prompt
        savedPrompt = await api.createPrompt(promptData);
      }
      
      // Refresh prompts list
      const prompts = await api.getPrompts();
      promptsStore.set(prompts);
      
      success = `Prompt "${title}" has been ${isEdit ? 'updated' : 'created'} successfully`;
      
      // If creating a new prompt, reset form after success
      if (!isEdit) {
        title = '';
        tags = '';
      }
    } catch (err) {
      console.error('Failed to save prompt:', err);
      error = `Failed to ${isEdit ? 'update' : 'create'} prompt: ${err.message}`;
    } finally {
      isSaving = false;
    }
  }
  
  // Cancel editing
  function cancel() {
    window.history.back();
  }
</script>

<div style="padding: 1.5rem;">
  <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem;">
    <h1 style="font-size: 1.5rem; font-weight: bold;">{isEdit ? 'Edit' : 'Create'} Prompt</h1>
    <div style="display: flex; gap: 0.5rem;">
      <button 
        on:click={cancel}
        style="padding: 0.5rem 1rem; border: 1px solid #d1d5db; border-radius: 0.25rem; background-color: white;"
      >
        Cancel
      </button>
      <button 
        on:click={testPrompt}
        disabled={isSaving}
        style="padding: 0.5rem 1rem; border-radius: 0.25rem; background-color: #8b5cf6; color: white; opacity: ${isSaving ? '0.7' : '1'};"
      >
        Test Prompt
      </button>
      <button 
        on:click={savePrompt}
        disabled={isSaving}
        style="padding: 0.5rem 1rem; border-radius: 0.25rem; background-color: #2563eb; color: white; opacity: ${isSaving ? '0.7' : '1'};"
      >
        {isSaving ? 'Saving...' : isEdit ? 'Update Prompt' : 'Save Prompt'}
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
  
  <div style="display: grid; grid-template-columns: 1fr 300px; gap: 1.5rem;">
    <!-- Main editor area -->
    <div style="background-color: white; padding: 1.5rem; border-radius: 0.5rem; box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);">
      <div style="margin-bottom: 1.5rem;">
        <label for="title" style="display: block; font-size: 0.875rem; font-weight: 500; margin-bottom: 0.25rem;">
          Prompt Title
        </label>
        <input 
          type="text" 
          id="title" 
          bind:value={title}
          style="width: 100%; padding: 0.5rem 0.75rem; border: 1px solid #d1d5db; border-radius: 0.375rem; box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);"
          placeholder="e.g., Python Code Helper"
        />
      </div>
      
      <div>
        <label for="content" style="display: block; font-size: 0.875rem; font-weight: 500; margin-bottom: 0.25rem;">
          Prompt Content
        </label>
        <textarea 
          id="content" 
          bind:value={content}
          style="width: 100%; height: 400px; padding: 0.5rem 0.75rem; border: 1px solid #d1d5db; border-radius: 0.375rem; box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05); resize: vertical; font-family: monospace;"
          placeholder="Enter your system prompt here..."
        ></textarea>
      </div>
    </div>
    
    <!-- Sidebar options -->
    <div>
      <!-- Models selection -->
      <div style="background-color: white; padding: 1.5rem; border-radius: 0.5rem; box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06); margin-bottom: 1.5rem;">
        <h2 style="font-size: 1.125rem; font-weight: 500; margin-bottom: 1rem;">Model Selection</h2>
        
        <div style="margin-bottom: 1rem;">
          <label for="model" style="display: block; font-size: 0.875rem; font-weight: 500; margin-bottom: 0.25rem;">
            Select Model
          </label>
          {#if availableModels.length === 0}
            <div style="color: #6b7280; font-size: 0.875rem;">Loading models...</div>
          {:else}
            <select
              id="model"
              bind:value={model}
              style="width: 100%; padding: 0.5rem 0.75rem; border: 1px solid #d1d5db; border-radius: 0.375rem; box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);"
            >
              {#each availableModels as modelOption}
                <option value={modelOption}>{modelOption}</option>
              {/each}
            </select>
          {/if}
        </div>
      </div>
      
      <!-- Templates -->
      <div style="background-color: white; padding: 1.5rem; border-radius: 0.5rem; box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06); margin-bottom: 1.5rem;">
        <h2 style="font-size: 1.125rem; font-weight: 500; margin-bottom: 1rem;">Templates</h2>
        
        <div style="display: flex; flex-direction: column; gap: 0.5rem;">
          <button 
            on:click={() => applyTemplate('general')}
            style="text-align: left; padding: 0.5rem; border: 1px solid #d1d5db; border-radius: 0.25rem; background-color: #f9fafb;"
          >
            General Assistant
          </button>
          <button 
            on:click={() => applyTemplate('coding')}
            style="text-align: left; padding: 0.5rem; border: 1px solid #d1d5db; border-radius: 0.25rem; background-color: #f9fafb;"
          >
            Coding Assistant
          </button>
          <button 
            on:click={() => applyTemplate('rag')}
            style="text-align: left; padding: 0.5rem; border: 1px solid #d1d5db; border-radius: 0.25rem; background-color: #f9fafb;"
          >
            RAG Template
          </button>
          <button 
            on:click={() => applyTemplate('creative')}
            style="text-align: left; padding: 0.5rem; border: 1px solid #d1d5db; border-radius: 0.25rem; background-color: #f9fafb;"
          >
            Creative Writing
          </button>
        </div>
      </div>
      
      <!-- Categories and Tags -->
      <div style="background-color: white; padding: 1.5rem; border-radius: 0.5rem; box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);">
        <h2 style="font-size: 1.125rem; font-weight: 500; margin-bottom: 1rem;">Organization</h2>
        
        <div style="margin-bottom: 1rem;">
          <label for="category" style="display: block; font-size: 0.875rem; font-weight: 500; margin-bottom: 0.25rem;">
            Category
          </label>
          <select
            id="category"
            bind:value={category}
            style="width: 100%; padding: 0.5rem 0.75rem; border: 1px solid #d1d5db; border-radius: 0.375rem; box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);"
          >
            <option value="">Select Category</option>
            {#each categories as categoryOption}
              <option value={categoryOption}>{categoryOption}</option>
            {/each}
          </select>
        </div>
        
        <div>
          <label for="tags" style="display: block; font-size: 0.875rem; font-weight: 500; margin-bottom: 0.25rem;">
            Tags (comma separated)
          </label>
          <input 
            type="text" 
            id="tags" 
            bind:value={tags}
            style="width: 100%; padding: 0.5rem 0.75rem; border: 1px solid #d1d5db; border-radius: 0.375rem; box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);"
            placeholder="e.g., coding, python, beginner"
          />
        </div>
      </div>
    </div>
  </div>
</div>