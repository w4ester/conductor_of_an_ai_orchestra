<script lang="ts">
  import { onMount } from 'svelte';
  import { api } from '../lib/api';
  import { modelsStore } from '../lib/store';
  
  // Props
  export let modelName = '';
  export let isEdit = false; // true for edit, false for create
  
  // State
  let modelfile = '';
  let name = '';
  let isSaving = false;
  let error = '';
  let success = '';
  let availableModels = [];
  let activeTemplate = '';
  
  // Example templates
  const templates = {
    basic: `PARAMETER temperature 0.7
PARAMETER num_predict 500

SYSTEM You are a helpful AI assistant.`,
    rag: `PARAMETER temperature 0.7
PARAMETER num_predict 500

SYSTEM You are a helpful AI assistant. When answering questions, use the provided context.

TEMPLATE """{{.System}}

Context:
{{.Context}}

User: {{.Prompt}}
Assistant: """`,
    json: `PARAMETER temperature 0.2
PARAMETER num_predict 500

SYSTEM You are a helpful AI assistant that always responds in valid JSON format with a "response" field containing your answer.

TEMPLATE """{{.System}}

User: {{.Prompt}}
Assistant: """`,
  };
  
  // Apply a template
  function applyTemplate(templateName) {
    activeTemplate = templateName;
    if (templates[templateName]) {
      modelfile = templates[templateName];
    }
  }
  
  // Load available models for FROM directive
  async function loadAvailableModels() {
    // Try to fetch actual models from Ollama API
    try {
      // Direct fetch from Ollama API
      try {
        const response = await fetch('http://localhost:11434/api/tags');
        if (response.ok) {
          const data = await response.json();
          availableModels = data.models.map(model => model.name);
          console.log('Loaded models directly from Ollama API:', availableModels);
          return;
        }
      } catch (directError) {
        console.error('Failed to load models directly from Ollama:', directError);
      }
      
      // Fallback to hardcoded models if direct API fails
      console.log('Using fallback model list');
      availableModels = ['llama3', 'mistral', 'phi3', 'gemma', 'tinyllama', 'llama3:8b', 'llama3:70b', 'codellama', 'orca2', 'vicuna', 'llava', 'qwen', 'llama2', 'wizard-math', 'neural-chat'];
    } catch (error) {
      console.error('Failed to load models:', error);
    }
  }
  
  // Load model if editing
  async function loadModel() {
    if (isEdit && modelName) {
      try {
        name = modelName;
        
        // Direct API call to Ollama to get modelfile
        const response = await fetch(`http://localhost:11434/api/show`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            name: modelName
          })
        });
        
        if (!response.ok) {
          throw new Error('Failed to load modelfile');
        }
        
        const data = await response.json();
        modelfile = data.modelfile || '';
      } catch (err) {
        console.error('Failed to load model:', err);
        error = 'Failed to load model. Please try again.';
      }
    }
  }
  
  // Save or update model
  async function saveModel() {
    if (!name || !modelfile) {
      error = 'Model name and modelfile are required.';
      return;
    }
    
    error = '';
    success = '';
    isSaving = true;
    
    try {
      // Direct API call to Ollama to create/update model
      const response = await fetch('http://localhost:11434/api/create', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          name,
          modelfile
        })
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to create model');
      }
      
      // Refresh available models
      await loadAvailableModels();
      
      success = `Model ${name} ${isEdit ? 'updated' : 'created'} successfully!`;
      
      // Reset form if creating a new model
      if (!isEdit) {
        name = '';
        modelfile = '';
      }
    } catch (err) {
      console.error('Failed to save model:', err);
      error = `Failed to ${isEdit ? 'update' : 'create'} model: ${err.message || 'Unknown error'}`;
    } finally {
      isSaving = false;
    }
  }
  
  // Delete model
  async function deleteModel() {
    if (!isEdit || !modelName) return;
    
    // Simple confirmation
    if (!confirm(`Are you sure you want to delete the model ${modelName}?`)) {
      return;
    }
    
    error = '';
    success = '';
    isSaving = true;
    
    try {
      // Direct API call to Ollama to delete model
      const response = await fetch('http://localhost:11434/api/delete', {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          name: modelName
        })
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to delete model');
      }
      
      // Refresh available models
      await loadAvailableModels();
      
      success = `Model ${modelName} deleted successfully!`;
      
      // Navigate back to models page
      setTimeout(() => {
        window.location.hash = '#/models';
      }, 1000);
    } catch (err) {
      console.error('Failed to delete model:', err);
      error = `Failed to delete model: ${err.message || 'Unknown error'}`;
    } finally {
      isSaving = false;
    }
  }
  
  // Cancel and go back
  function cancel() {
    window.location.hash = '#/models';
  }
  
  // Download Modelfile
  function downloadModelfile() {
    const element = document.createElement('a');
    const file = new Blob([modelfile], {type: 'text/plain'});
    element.href = URL.createObjectURL(file);
    element.download = `${name || 'modelfile'}.modelfile`;
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
  }
  
  // Copy Modelfile to clipboard
  function copyModelfile() {
    navigator.clipboard.writeText(modelfile).then(() => {
      // Could show a toast notification here
      console.log('Modelfile copied to clipboard');
    }).catch(err => {
      console.error('Failed to copy modelfile:', err);
    });
  }
  
  // Load on mount
  onMount(() => {
    loadAvailableModels();
    if (isEdit) {
      loadModel();
    }
  });
  
  // Helper function to set the base model in the modelfile
  function setBaseModel(selectedModel) {
    const lines = modelfile.split('\n');
    const fromLineIndex = lines.findIndex(line => line.trim().startsWith('FROM'));
    
    if (fromLineIndex >= 0) {
      // Replace existing FROM line
      lines[fromLineIndex] = `FROM ${selectedModel}`;
    } else {
      // Add FROM as first line
      lines.unshift(`FROM ${selectedModel}`);
    }
    
    modelfile = lines.join('\n');
  }
</script>

<div class="dashboard-section">
  <div class="flex justify-between items-center mb-8">
    <h1 class="text-3xl font-bold text-primary">{isEdit ? 'Edit' : 'Create'} Model</h1>
    <div class="flex gap-3">
      <button 
        class="btn btn-secondary" 
        on:click={cancel}
      >
        Cancel
      </button>
      {#if isEdit}
        <button 
          class="btn btn-danger" 
          on:click={deleteModel} 
          disabled={isSaving}
        >
          Delete Model
        </button>
      {/if}
      <button 
        class="btn btn-primary" 
        on:click={saveModel} 
        disabled={isSaving}
      >
        {isSaving ? 'Saving...' : isEdit ? 'Update Model' : 'Create Model'}
      </button>
    </div>
  </div>
  
  {#if error}
    <div class="alert alert-danger mb-6" role="alert">
      <span>{error}</span>
    </div>
  {/if}
  
  {#if success}
    <div class="alert alert-success mb-6" role="alert">
      <span>{success}</span>
    </div>
  {/if}
  
  <div class="content-card mb-8">
    <div class="form-group">
      <label for="name" class="form-label">Model Name</label>
      <input 
        type="text" 
        id="name" 
        bind:value={name}
        disabled={isEdit}
        class="form-input"
        placeholder="my-custom-assistant"
      />
      <p class="text-xs text-gray-400 mt-2">
        This will be the name used to reference your model, e.g., "ollama run my-custom-assistant"
      </p>
    </div>
    
    <div class="form-group">
      <label class="form-label">Template</label>
      <div class="flex gap-3 mb-2">
        <button 
          class={`template-btn ${activeTemplate === 'basic' ? 'active' : ''}`}
          on:click={() => {
            applyTemplate('basic');
          }}
        >
          Basic Assistant
        </button>
        <button 
          class={`template-btn ${activeTemplate === 'rag' ? 'active' : ''}`}
          on:click={() => {
            applyTemplate('rag');
          }}
        >
          RAG Template
        </button>
        <button 
          class={`template-btn ${activeTemplate === 'json' ? 'active' : ''}`}
          on:click={() => {
            applyTemplate('json');
          }}
        >
          JSON Response
        </button>
      </div>
    </div>
    
    <div class="form-group">
      <label for="baseModel" class="form-label">Base Model</label>
      <div class="relative">
        <select 
          id="baseModel" 
          class="form-select"
          on:change={(e) => setBaseModel(e.target.value)}
        >
          <option value="" disabled selected>Select a base model...</option>
          {#if availableModels.length === 0}
            <option disabled>Loading models...</option>
          {:else}
            {#each availableModels as model}
              <option value={model}>{model}</option>
            {/each}
          {/if}
        </select>
        <div class="select-arrow">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
          </svg>
        </div>
      </div>
      <p class="text-xs text-gray-400 mt-2">
        Select a base model to use with the "FROM" directive in your Modelfile
      </p>
    </div>

    <div class="form-group">
      <label for="modelfile" class="form-label">Modelfile</label>
      <div class="modelfile-container">
        <div class="modelfile-header">
          <span class="font-mono text-sm">Modelfile</span>
          <div class="flex gap-2">
            <button class="icon-btn tooltip-container" title="Download Modelfile" on:click={downloadModelfile}>
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12"></path>
              </svg>
              <span class="tooltip">Download Modelfile</span>
            </button>
            <button class="icon-btn tooltip-container" title="Copy Modelfile" on:click={copyModelfile}>
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"></path>
              </svg>
              <span class="tooltip">Copy Modelfile</span>
            </button>
          </div>
        </div>
        <textarea 
          id="modelfile" 
          bind:value={modelfile}
          rows="12" 
          class="modelfile-textarea"
          placeholder="FROM llama3:8b

PARAMETER temperature 0.7
PARAMETER top_p 0.9

SYSTEM You are a helpful assistant..."
        ></textarea>
      </div>
      <p class="text-xs text-gray-400 mt-2">
        The Modelfile defines your model's behavior, parameters, and system prompt
      </p>
    </div>
  </div>

  <div class="content-card mb-8">
    <h2 class="section-title mb-4">Available Base Models</h2>
    <div class="model-grid">
      {#if availableModels.length === 0}
        <div class="col-span-full empty-state">
          <div class="text-gray-400">Loading available models...</div>
        </div>
      {:else}
        {#each availableModels.slice(0, 8) as model}
          <div 
            class="model-card"
            on:click={() => setBaseModel(model)}
          >
            <div class="model-name">{model}</div>
            <div class="model-info">{model.includes(':') ? model.split(':')[0] : 'Base model'}</div>
          </div>
        {/each}
      {/if}
    </div>
  </div>

  <div class="content-card mb-8">
    <h2 class="section-title mb-4">Chat Preview</h2>
    <div class="chat-preview">
      <div class="chat-message user">
        <div class="chat-bubble">Hello, can you help me with a programming question?</div>
      </div>
      <div class="chat-message assistant">
        <div class="chat-bubble">Of course! I'd be happy to help with your programming question. What specifically would you like assistance with?</div>
      </div>
    </div>
    <p class="text-xs text-gray-400 mt-2">
      Preview of how your custom model might respond based on your configuration
    </p>
  </div>

  <div class="content-card">
    <h2 class="section-title mb-4">Modelfile Reference</h2>
    <div class="reference-grid">
      <div class="reference-item">
        <div class="reference-command">FROM</div>
        <div class="reference-desc">Base model to use (required)</div>
      </div>
      <div class="reference-item">
        <div class="reference-command">PARAMETER</div>
        <div class="reference-desc">Set a parameter for the model (e.g., temperature)</div>
      </div>
      <div class="reference-item">
        <div class="reference-command">SYSTEM</div>
        <div class="reference-desc">System prompt for the model</div>
      </div>
      <div class="reference-item">
        <div class="reference-command">TEMPLATE</div>
        <div class="reference-desc">Custom prompt template format</div>
      </div>
    </div>
    <div class="mt-4">
      <a href="https://github.com/ollama/ollama/blob/main/docs/modelfile.md" target="_blank" class="doc-link">
        View full Modelfile documentation →
      </a>
    </div>
  </div>
</div>

<style>
  .form-group {
    margin-bottom: 1.5rem;
  }
  
  .form-label {
    display: block;
    margin-bottom: 0.5rem;
    font-weight: 500;
    color: var(--text-primary);
    font-size: 1.125rem;
  }
  
  .form-input, 
  .form-textarea,
  .form-select {
    width: 100%;
    padding: 0.75rem;
    background-color: var(--surface-1);
    border: 1px solid var(--border-primary);
    border-radius: var(--radius-md);
    color: var(--text-primary);
    transition: all var(--transition-base);
  }
  
  .form-input:focus, 
  .form-textarea:focus,
  .form-select:focus {
    border-color: var(--primary-500);
    outline: none;
    box-shadow: 0 0 0 2px var(--primary-200);
  }
  
  .form-textarea {
    min-height: 100px;
    font-family: monospace;
  }
  
  .form-select {
    appearance: none;
    padding-right: 2.5rem;
  }
  
  .select-arrow {
    position: absolute;
    right: 0.75rem;
    top: 50%;
    transform: translateY(-50%);
    color: var(--text-secondary);
    pointer-events: none;
  }
  
  .modelfile-container {
    border: 2px solid var(--primary-400);
    border-radius: var(--radius-md);
    overflow: hidden;
    background-color: var(--surface-1);
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  }
  
  .modelfile-header {
    background-color: var(--surface-2);
    padding: 0.5rem 1rem;
    border-bottom: 1px solid var(--border-primary);
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  
  .modelfile-textarea {
    width: 100%;
    padding: 1rem;
    border: none;
    background-color: var(--surface-1);
    color: var(--text-primary);
    font-family: 'Monaco', 'Consolas', 'Source Code Pro', monospace;
    font-size: 0.875rem;
    min-height: 300px;
    resize: vertical;
    line-height: 1.5;
  }
  
  .modelfile-textarea:focus {
    outline: none;
  }
  
  .icon-btn {
    padding: 0.25rem;
    border-radius: var(--radius-sm);
    color: var(--text-secondary);
    background-color: transparent;
    transition: all var(--transition-base);
  }
  
  .icon-btn:hover {
    background-color: var(--surface-3);
    color: var(--text-primary);
  }
  
  .template-btn {
    padding: 0.5rem 1rem;
    background-color: var(--surface-2);
    color: var(--text-primary);
    border-radius: var(--radius-md);
    font-size: 0.875rem;
    font-weight: 500;
    transition: all var(--transition-base);
    border: 1px solid var(--border-primary);
  }
  
  .template-btn:hover {
    background-color: var(--surface-3);
  }
  
  .template-btn.active {
    background-color: var(--primary-600);
    color: white;
    border-color: var(--primary-700);
  }
  
  .section-title {
    color: var(--text-primary);
    font-size: 1.25rem;
    font-weight: 600;
  }
  
  .model-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 1rem;
  }
  
  @media (min-width: 640px) {
    .model-grid {
      grid-template-columns: repeat(3, 1fr);
    }
  }
  
  @media (min-width:.col-span-full {
  grid-column: 1 / -1;
}

.empty-state {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 2rem;
  text-align: center;
}

.reference-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 0.75rem;
}

@media (min-width: 640px) {
  .reference-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

.reference-item {
  padding: 0.75rem;
  background-color: var(--surface-2);
  border-radius: var(--radius-md);
  border: 1px solid var(--border-primary);
}

.reference-command {
  font-family: monospace;
  font-weight: 600;
  color: var(--primary-500);
  margin-bottom: 0.25rem;
}

.reference-desc {
  font-size: 0.875rem;
  color: var(--text-secondary);
}

.doc-link {
  color: var(--primary-500);
  font-size: 0.875rem;
  font-weight: 500;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  transition: color var(--transition-base);
}

.doc-link:hover {
  color: var(--primary-600);
  text-decoration: underline;
}

.chat-preview {
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-md);
  padding: 1rem;
  max-height: 300px;
  overflow-y: auto;
  background-color: var(--surface-1);
}

.chat-message {
  margin-bottom: 1rem;
  display: flex;
}

.chat-message.user {
  justify-content: flex-end;
}

.chat-bubble {
  padding: 0.75rem 1rem;
  border-radius: 1rem;
  max-width: 80%;
  word-wrap: break-word;
}

.chat-message.user .chat-bubble {
  background-color: var(--primary-600);
  color: white;
  border-top-right-radius: 0.25rem;
}

.chat-message.assistant .chat-bubble {
  background-color: var(--surface-2);
  color: var(--text-primary);
  border-top-left-radius: 0.25rem;
}

.model-card {
  padding: 0.75rem;
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-md);
  background-color: var(--surface-1);
  cursor: pointer;
  transition: all var(--transition-base);
}

.model-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
  border-color: var(--primary-400);
}

.model-name {
  font-weight: 500;
  color: var(--primary-500);
  margin-bottom: 0.25rem;
}

.model-info {
  font-size: 0.75rem;
  color: var(--text-secondary);
}

.tooltip-container {
  position: relative;
}

.tooltip {
  visibility: hidden;
  position: absolute;
  bottom: -30px;
  left: 50%;
  transform: translateX(-50%);
  background-color: var(--surface-3);
  color: var(--text-primary);
  text-align: center;
  border-radius: 4px;
  padding: 4px 8px;
  font-size: 0.75rem;
  white-space: nowrap;
  z-index: 100;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
  opacity: 0;
  transition: opacity 0.3s;
}

.tooltip-container:hover .tooltip {
  visibility: visible;
  opacity: 1;
}

.mb-8 {
  margin-bottom: 2rem;
}

.mb-6 {
  margin-bottom: 1.5rem;
}

.mb-4 {
  margin-bottom: 1rem;
}

.mb-2 {
  margin-bottom: 0.5rem;
}

.mt-2 {
  margin-top: 0.5rem;
}

.mt-4 {
  margin-top: 1rem;
}

.gap-3 {
  gap: 0.75rem;
}

.gap-2 {
  gap: 0.5rem;
}

.flex {
  display: flex;
}

.justify-between {
  justify-content: space-between;
}

.items-center {
  align-items: center;
}

.text-primary {
  color: var(--primary-600);
}
</style>