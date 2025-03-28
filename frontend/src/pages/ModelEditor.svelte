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
  let selectedBaseModel = '';
  
  // Example templates
  const templates = {
    basic: `PARAMETER temperature 0.7
PARAMETER num_predict 500

SYSTEM You are a helpful AI assistant.`,
    rag: `PARAMETER temperature 0.7
PARAMETER num_predict 500

SYSTEM You are a helpful AI assistant. When answering questions, use the provided context.

TEMPLATE \"\"\"{{.System}}

Context:
{{.Context}}

User: {{.Prompt}}
Assistant: \"\"\"`,
    json: `PARAMETER temperature 0.2
PARAMETER num_predict 500

SYSTEM You are a helpful AI assistant that always responds in valid JSON format with a \"response\" field containing your answer.

TEMPLATE \"\"\"{{.System}}

User: {{.Prompt}}
Assistant: \"\"\"`,
    tools: `PARAMETER temperature 0.7
PARAMETER num_predict 500

SYSTEM You are a helpful AI assistant with access to tools. When a user asks something that requires web search, use the 'search' tool.

TOOL search {
  "description": "Search the internet for current information",
  "input_schema": {
    "type": "object",
    "properties": {
      "query": {
        "type": "string",
        "description": "The search query string"
      }
    },
    "required": ["query"]
  }
}

TEMPLATE """{{.System}}

User: {{.Prompt}}
Assistant: {{.Response}}"""`,
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
        
        // Extract base model if available
        const fromMatch = modelfile.match(/^FROM\\s+(\\S+)/m);
        if (fromMatch && fromMatch[1]) {
          selectedBaseModel = fromMatch[1];
        }
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
      // Show a toast notification (future enhancement)
      console.log('Modelfile copied to clipboard');
      const toast = document.getElementById('toast-notification');
      if (toast) {
        toast.classList.remove('hidden');
        setTimeout(() => {
          toast.classList.add('hidden');
        }, 3000);
      }
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
    selectedBaseModel = selectedModel;
    const lines = modelfile.split('\
');
    const fromLineIndex = lines.findIndex(line => line.trim().startsWith('FROM'));
    
    if (fromLineIndex >= 0) {
      // Replace existing FROM line
      lines[fromLineIndex] = `FROM ${selectedModel}`;
    } else {
      // Add FROM as first line
      lines.unshift(`FROM ${selectedModel}`);
    }
    
    modelfile = lines.join('\
');
  }
  
  // Get model category for displaying
  function getModelCategory(model) {
    if (model.includes('llama3')) return 'Llama 3';
    if (model.includes('mistral')) return 'Mistral';
    if (model.includes('gemma')) return 'Gemma';
    if (model.includes('codellama')) return 'Code Llama';
    if (model.includes('llama2')) return 'Llama 2';
    if (model.includes('phi')) return 'Phi';
    return model.split(':')[0] || 'Base Model';
  }
</script>

<div class="page-container">
  <div id="toast-notification" class="toast-notification hidden">
    <div class="toast-content">
      <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
      </svg>
      <span>Modelfile copied to clipboard!</span>
    </div>
  </div>
  
  <div class="page-header">
    <h1 class="page-title">{isEdit ? 'Edit' : 'Create'} Model</h1>
    <div class="action-buttons">
      <button 
        class="btn btn-cancel" 
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
          <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
          </svg>
          Delete Model
        </button>
      {/if}
      <button 
        class="btn btn-create" 
        on:click={saveModel} 
        disabled={isSaving}
      >
        {#if isSaving}
          <svg class="animate-spin w-5 h-5 mr-2" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          Saving...
        {:else}
          <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
          </svg>
          {isEdit ? 'Update Model' : 'Create Model'}
        {/if}
      </button>
    </div>
  </div>
  
  {#if error}
    <div class="alert alert-danger" role="alert">
      <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
      </svg>
      <span>{error}</span>
    </div>
  {/if}
  
  {#if success}
    <div class="alert alert-success" role="alert">
      <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
      </svg>
      <span>{success}</span>
    </div>
  {/if}
  
  <div class="editor-layout">
    <!-- Main Content Area: Modelfile Editor -->
    <div class="modelfile-editor-container">
      <div class="card modelfile-card">
        <div class="card-header">
          <h2 class="card-title">Modelfile</h2>
          <div class="card-actions">
            <button class="icon-btn" title="Download Modelfile" on:click={downloadModelfile}>
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"></path>
              </svg>
            </button>
            <button class="icon-btn" title="Copy Modelfile" on:click={copyModelfile}>
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"></path>
              </svg>
            </button>
          </div>
        </div>
        <div class="card-body no-padding">
          <div class="code-editor">
            <textarea 
              id="modelfile" 
              bind:value={modelfile}
              class="code-textarea"
              placeholder="FROM llama3:8b

PARAMETER temperature 0.7
PARAMETER top_p 0.9

SYSTEM You are a helpful assistant..."
            ></textarea>
          </div>
        </div>
      </div>
    </div>

    <!-- Right Sidebar: Configuration and Reference -->
    <div class="sidebar">
      <div class="card">
        <div class="card-header">
          <h2 class="card-title">Model Configuration</h2>
        </div>
        <div class="card-body">
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
            <p class="help-text">
              This will be the name used to reference your model, e.g., "ollama run my-custom-assistant"
            </p>
          </div>
          
          <div class="form-group">
            <label class="form-label">Template</label>
            <div class="template-buttons">
              <button 
                class={`template-btn ${activeTemplate === 'basic' ? 'active' : ''}`}
                on:click={() => applyTemplate('basic')}
              >
                <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"></path>
                </svg>
                Basic Assistant
              </button>
              <button 
                class={`template-btn ${activeTemplate === 'rag' ? 'active' : ''}`}
                on:click={() => applyTemplate('rag')}
              >
                <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0112.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z"></path>
                </svg>
                RAG Template
              </button>
              <button 
                class={`template-btn ${activeTemplate === 'json' ? 'active' : ''}`}
                on:click={() => applyTemplate('json')}
              >
                <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z"></path>
              </svg>
              JSON Response
              </button>
              <button 
                class={`template-btn ${activeTemplate === 'tools' ? 'active' : ''}`}
                on:click={() => applyTemplate('tools')}
              >
                <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"></path>
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
                </svg>
                Tools Template
              </button>
            </div>
          </div>
          
          <div class="form-group">
            <label for="baseModel" class="form-label">Base Model</label>
            <div class="select-wrapper">
              <select 
                id="baseModel"
                class="form-select"
                bind:value={selectedBaseModel}
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
              <div class="select-icon">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
                </svg>
              </div>
            </div>
            <p class="help-text">
              Select a base model to use with the "FROM" directive in your Modelfile
            </p>
          </div>
        </div>
      </div>
      
      <div class="card models-card">
        <div class="card-header">
          <h2 class="card-title">Popular Base Models</h2>
        </div>
        <div class="card-body">
          <div class="model-grid">
            {#if availableModels.length === 0}
              <div class="loading-state">
                <svg class="animate-spin w-8 h-8 text-primary" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                <span>Loading models...</span>
              </div>
            {:else}
              {#each availableModels.slice(0, 8) as model}
                <div 
                  class={`model-item ${selectedBaseModel === model ? 'selected' : ''}`}
                  on:click={() => setBaseModel(model)}
                >
                  <div class="model-icon">
                    {model.charAt(0).toUpperCase()}
                  </div>
                  <div class="model-details">
                    <div class="model-name">{model}</div>
                    <div class="model-category">{getModelCategory(model)}</div>
                  </div>
                  {#if selectedBaseModel === model}
                    <div class="model-selected-indicator">
                      <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                      </svg>
                    </div>
                  {/if}
                </div>
              {/each}
            {/if}
          </div>
        </div>
      </div>

      <div class="card reference-card">
        <div class="card-header">
          <h2 class="card-title">Modelfile Reference</h2>
        </div>
        <div class="card-body">
          <div class="reference-grid">
            <div class="reference-item">
              <div class="reference-command">FROM</div>
              <div class="reference-desc">Base model to use (required)</div>
              <div class="reference-example">FROM llama3:8b</div>
            </div>
            <div class="reference-item">
              <div class="reference-command">PARAMETER</div>
              <div class="reference-desc">Set inference parameters</div>
              <div class="reference-example">PARAMETER temperature 0.7</div>
            </div>
            <div class="reference-item">
              <div class="reference-command">SYSTEM</div>
              <div class="reference-desc">System prompt for the model</div>
              <div class="reference-example">SYSTEM You are a helpful assistant.</div>
            </div>
            <div class="reference-item">
              <div class="reference-command">TEMPLATE</div>
              <div class="reference-desc">Custom prompt template format</div>
              <div class="reference-example">TEMPLATE """&#123;&#123;.System&#125;&#125;

User: &#123;&#123;.Prompt&#125;&#125;
Assistant: """</div>
            </div>
            <div class="reference-item">
              <div class="reference-command">TOOL</div>
              <div class="reference-desc">Define a tool the model can use</div>
              <div class="reference-example">TOOL search &#123;
  "description": "Search the internet",
  "input_schema": &#123;
    "type": "object",
    "properties": &#123;
      "query": &#123;"type": "string"&#125;
    &#125;
  &#125;
&#125;</div>
            </div>
          </div>
          <a href="https://github.com/ollama/ollama/blob/main/docs/modelfile.md" target="_blank" class="doc-link">
            <span>View full Modelfile documentation</span>
            <svg class="w-5 h-5 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"></path>
            </svg>
          </a>
        </div>
      </div>
    </div>
  </div>
</div>

<style>
  .page-container {
    max-width: 1400px;
    margin: 0 auto;
    padding: 1.5rem;
  }
  
  .page-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1.5rem;
    padding-bottom: 1rem;
    border-bottom: 2px solid var(--border-primary);
  }
  
  .page-title {
    font-size: 2rem;
    font-weight: 700;
    color: var(--primary-600);
    margin: 0;
  }
  
  .action-buttons {
    display: flex;
    gap: 1rem;
  }
  
  .alert {
    display: flex;
    align-items: center;
    padding: 1rem;
    border-radius: 0.5rem;
    margin-bottom: 1.5rem;
    font-weight: 500;
  }
  
  .alert svg {
    flex-shrink: 0;
    width: 1.25rem;
    height: 1.25rem;
    margin-right: 0.75rem;
  }
  
  .alert-danger {
    background-color: rgba(220, 38, 38, 0.1);
    color: rgb(185, 28, 28);
    border: 1px solid rgba(220, 38, 38, 0.3);
  }
  
  .alert-success {
    background-color: rgba(16, 185, 129, 0.1);
    color: rgb(5, 150, 105);
    border: 1px solid rgba(16, 185, 129, 0.3);
  }
  
  .editor-layout {
    display: grid;
    grid-template-columns: 1fr 360px;
    gap: 1.5rem;
  }
  
  @media (max-width: 1024px) {
    .editor-layout {
      grid-template-columns: 1fr;
    }
  }
  
  .card {
    background-color: var(--surface-1);
    border-radius: 0.75rem;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    margin-bottom: 1.5rem;
    border: 1px solid var(--border-primary);
    overflow: hidden;
  }
  
  .modelfile-card {
    height: calc(100vh - 200px);
    min-height: 500px;
    display: flex;
    flex-direction: column;
  }
  
  .models-card, .reference-card {
    margin-bottom: 1.5rem;
  }
  
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1rem 1.25rem;
    border-bottom: 1px solid var(--border-primary);
    background-color: var(--surface-2);
  }
  
  .card-title {
    font-size: 1.25rem;
    font-weight: 600;
    margin: 0;
    color: var(--text-primary);
  }
  
  .card-actions {
    display: flex;
    gap: 0.5rem;
  }
  
  .card-body {
    padding: 1.25rem;
  }
  
  .card-body.no-padding {
    padding: 0;
    flex-grow: 1;
  }
  
  .form-group {
    margin-bottom: 1.5rem;
  }
  
  .form-group:last-child {
    margin-bottom: 0;
  }
  
  .form-label {
    display: block;
    margin-bottom: 0.5rem;
    font-weight: 600;
    color: var(--text-primary);
    font-size: 1rem;
  }
  
  .form-input,
  .form-select {
    width: 100%;
    padding: 0.875rem 1rem;
    border: 2px solid var(--border-primary);
    border-radius: 0.5rem;
    background-color: var(--surface-1);
    color: var(--text-primary);
    font-size: 1rem;
    transition: all 0.2s ease;
  }
  
  .form-input:focus, 
  .form-select:focus {
    border-color: var(--primary-500);
    outline: none;
    box-shadow: 0 0 0 3px var(--primary-200);
  }
  .template-btn:hover {
    background-color: var(--surface-3);
    transform: translateY(-1px);
  }
  
  .template-btn.active {
    background-color: var(--primary-600);
    color: white;
    border-color: var(--primary-700);
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  }
  
  .code-editor {
    height: 100%;
    border-radius: 0;
    background-color: var(--code-bg);
    display: flex;
    flex-direction: column;
  }
  
  .code-textarea {
    width: 100%;
    height: 100%;
    padding: 1.5rem;
    border: none;
    background-color: var(--surface-1);
    color: var(--text-primary);
    font-family: 'Menlo', 'Monaco', 'Consolas', 'Source Code Pro', monospace;
    font-size: 1rem;
    line-height: 1.6;
    resize: none;
  }
  
  .code-textarea:focus {
    outline: none;
  }
  
  .model-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 1rem;
  }
  
  .model-item {
    display: flex;
    align-items: center;
    padding: 0.75rem;
    background-color: var(--surface-2);
    border-radius: 0.5rem;
    border: 2px solid var(--border-primary);
    cursor: pointer;
    transition: all 0.2s ease;
    position: relative;
  }
  
  .model-item:hover {
    background-color: var(--surface-3);
    transform: translateY(-2px);
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
  }
  
  .model-item.selected {
    border-color: var(--primary-500);
    background-color: rgba(59, 130, 246, 0.1);
    box-shadow: 0 0 0 2px var(--primary-200);
  }
  
  .model-icon {
    width: 2.5rem;
    height: 2.5rem;
    background-color: var(--primary-600);
    border-radius: 0.5rem;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-weight: 600;
    font-size: 1.125rem;
    margin-right: 0.75rem;
  }
  
  .model-details {
    flex: 1;
    overflow: hidden;
  }
  
  .model-name {
    font-weight: 600;
    font-size: 0.875rem;
    margin-bottom: 0.25rem;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
  
  .model-category {
    font-size: 0.75rem;
    color: var(--text-secondary);
  }
  
  .model-selected-indicator {
    position: absolute;
    top: 0.5rem;
    right: 0.5rem;
    color: var(--primary-500);
  }
  
  .loading-state {
    grid-column: 1 / -1;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 2rem;
    color: var(--text-secondary);
    gap: 1rem;
  }
  
  .reference-grid {
    display: grid;
    grid-template-columns: 1fr;
    gap: 0.75rem;
  }
  
  .reference-item {
    padding: 0.75rem;
    background-color: var (--surface-2);
    border-radius: 0.5rem;
    border: 1px solid var(--border-primary);
  }
  
  .reference-command {
    font-family: monospace;
    font-weight: 600;
    color: var(--primary-500);
    margin-bottom: 0.25rem;
    font-size: 1rem;
  }
  
  .reference-desc {
    font-size: 0.875rem;
    color: var(--text-secondary);
  }
  
  .reference-example {
    font-family: monospace;
    font-size: 0.75rem;
    margin-top: 0.5rem;
    padding: 0.5rem;
    background-color: var(--surface-1);
    border-radius: 0.375rem;
    border: 1px solid var(--border-primary);
    white-space: nowrap;
    overflow: auto;
  }
  
  .doc-link {
    color: var(--primary-500);
    font-size: 0.875rem;
    font-weight: 600;
    text-decoration: none;
    display: inline-flex;
    align-items: center;
    transition: color 0.2s ease;
    margin-top: 1.25rem;
  }
  
  .doc-link:hover {
    color: var(--primary-600);
    text-decoration: underline;
  }
  
  .icon-btn {
    padding: 0.5rem;
    border-radius: 0.375rem;
    color: var(--text-secondary);
    background-color: transparent;
    transition: all 0.2s ease;
  }
  
  .icon-btn:hover {
    background-color: var(--surface-3);
    color: var(--text-primary);
  }
  
  .toast-notification {
    position: fixed;
    top: 1rem;
    right: 1rem;
    z-index: 100;
    transition: all 0.3s ease;
  }
  
  .toast-notification.hidden {
    transform: translateY(-100%);
    opacity: 0;
  }
  
  .toast-content {
    display: flex;
    align-items: center;
    background-color: var(--surface-3);
    color: var(--text-primary);
    padding: 0.75rem 1rem;
    border-radius: 0.5rem;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    border-left: 4px solid var(--primary-500);
  }
  
  .btn {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    padding: 0.75rem 1.5rem;
    font-weight: 600;
    border-radius: 0.5rem;
    cursor: pointer;
    transition: all 0.2s ease;
    font-size: 1rem;
    letter-spacing: 0.025em;
  }
  
  .btn-create {
    background-color: var(--primary-600);
    color: white;
    border: none;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  }
  
  .btn-create:hover:not(:disabled) {
    background-color: var(--primary-700);
    transform: translateY(-1px);
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  }
  
  .btn-cancel {
    background-color: transparent;
    color: var (--text-primary);
    border: 2px solid var(--border-primary);
  }
  
  .btn-cancel:hover {
    background-color: var(--surface-2);
  }
  
  .btn-danger {
    background-color: rgba(239, 68, 68, 0.1);
    color: rgb(220, 38, 38);
    border: 1px solid rgba(239, 68, 68, 0.3);
  }
  
  .btn-danger:hover:not(:disabled) {
    background-color: rgb(220, 38, 38);
    color: white;
  }
  
  .btn:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
  
  /* Focus on the Modelfile editor */
  .modelfile-editor-container {
    display: flex;
    flex-direction: column;
  }
</style>