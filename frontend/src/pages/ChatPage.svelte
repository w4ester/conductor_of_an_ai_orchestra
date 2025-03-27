<script lang="ts">
  import { onMount } from 'svelte';
  import { api } from '../lib/api';
  import { 
    modelsStore, 
    promptsStore, 
    toolsStore, 
    embeddingsStore, 
    authStore
  } from '../lib/store';
  import Card from '../components/ui/Card.svelte';
  import { fade, fly } from 'svelte/transition';

  // Simple markdown formatter (will be replaced by marked when available)
  function simpleMarkdownFormat(text) {
    // Handle code blocks
    text = text.replace(/```([a-z]*)\n([\s\S]*?)```/g, '<pre><code class="language-$1">$2</code></pre>');
    
    // Handle inline code
    text = text.replace(/`([^`]+)`/g, '<code>$1</code>');
    
    // Handle bold
    text = text.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
    
    // Handle italic
    text = text.replace(/\*([^*]+)\*/g, '<em>$1</em>');
    
    // Handle links
    text = text.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2">$1</a>');
    
    // Handle paragraphs (simplified)
    text = '<p>' + text.replace(/\n\n/g, '</p><p>') + '</p>';
    
    return text;
  }

  // State management
  let selectedModel = '';
  let selectedPrompt = '';
  let selectedTools = [];
  let selectedEmbedding = '';
  let userInput = '';
  let messages = [];
  let isLoading = false;
  let error = '';
  let showSettings = false;
  
  // Settings
  let temperature = 0.7;
  let maxTokens = 1000;
  let useRAG = false;
  let useTools = false;
  
  // References to libraries loaded via CDN
  let markedLib;
  let hljs;
  
  // Get data from stores
  $: availableModels = $modelsStore;
  $: availablePrompts = $promptsStore;
  $: availableTools = $toolsStore;
  $: availableEmbeddings = $embeddingsStore;
  
  // Initialize with default selections if available
  onMount(async () => {
    try {
      // Load marked and highlight.js from CDN
      await Promise.all([
        loadScript('https://cdnjs.cloudflare.com/ajax/libs/marked/4.3.0/marked.min.js'),
        loadScript('https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.8.0/highlight.min.js')
      ]);
      
      // Assign global variables once loaded
      markedLib = window.marked;
      hljs = window.hljs;
      
      // Configure marked to use highlight.js
      if (markedLib && hljs) {
        markedLib.setOptions({
          highlight: function(code, lang) {
            if (lang && hljs.getLanguage(lang)) {
              return hljs.highlight(lang, code).value;
            }
            return hljs.highlightAuto(code).value;
          },
          breaks: true,
          gfm: true
        });
      }
      
      // Load CSS for highlight.js
      loadCSS('https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.8.0/styles/github.min.css');
      
      // Look for model parameter in URL
      const urlParams = new URLSearchParams(window.location.hash.split('?')[1] || '');
      const modelParam = urlParams.get('model');
      
      // Load models if not already loaded
      if (availableModels.length === 0) {
        const models = await api.getModels();
        modelsStore.set(models);
        
        // Set default model if available
        if (models.length > 0) {
          // If URL has model parameter, use that, otherwise use first model
          if (modelParam && models.some(m => m.name === modelParam)) {
            selectedModel = modelParam;
          } else {
            selectedModel = models[0].name;
          }
        }
      } else if (availableModels.length > 0) {
        // If URL has model parameter, use that, otherwise use first model
        if (modelParam && availableModels.some(m => m.name === modelParam)) {
          selectedModel = modelParam;
        } else {
          selectedModel = availableModels[0].name;
        }
      }
    } catch (err) {
      console.error("Error initializing chat page:", err);
      error = "Failed to initialize: " + err.message;
    }
  });

  // Helper function to load scripts dynamically
  function loadScript(src) {
    return new Promise((resolve, reject) => {
      const script = document.createElement('script');
      script.src = src;
      script.onload = resolve;
      script.onerror = reject;
      document.head.appendChild(script);
    });
  }
  
  // Helper function to load CSS dynamically
  function loadCSS(src) {
    const link = document.createElement('link');
    link.rel = 'stylesheet';
    link.href = src;
    document.head.appendChild(link);
  }
  
  // Handle chat submission
  async function sendMessage() {
    if (!userInput.trim() || isLoading) return;
    
    const userMessage = { role: 'user', content: userInput };
    messages = [...messages, userMessage];
    
    const currentInput = userInput;
    userInput = '';
    error = '';
    isLoading = true;
    
    try {
      // Convert chat format to generate format
      let prompt = userMessage.content;
      
      // Add system prompt if selected
      if (selectedPrompt) {
        prompt = `${selectedPrompt}\n\n${prompt}`;
      }
      
      // Add context from previous messages if there are any
      if (messages.length > 1) {
        const context = messages
          .slice(0, -1) // Exclude the last message (we just added it)
          .map(m => `${m.role === 'user' ? 'User' : 'Assistant'}: ${m.content}`)
          .join('\n\n');
        prompt = `${context}\n\nUser: ${prompt}\n\nAssistant:`;
      }
      
      // Only chat should use Ollama's direct API format
      const response = await fetch('http://localhost:11434/api/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          model: selectedModel,
          prompt: prompt,
          stream: false,
          options: {
            temperature: temperature,
            num_predict: maxTokens
          }
        })
      });
      
      if (!response.ok) {
        throw new Error('Failed to get response from Ollama');
      }
      
      const data = await response.json();
      messages = [...messages, { role: 'assistant', content: data.response }];
    } catch (err) {
      console.error('Chat error:', err);
      error = `Error: ${err.message || 'Failed to get response'}`;
    } finally {
      isLoading = false;
    }
  }
</script>

<div class="chat-layout">
  <!-- Chat Header -->
  <header class="chat-header">
    <h2 class="chat-title">AI Assistant</h2>
    <button class="settings-button" on:click={() => showSettings = !showSettings} aria-label="Settings">
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <circle cx="12" cy="12" r="3"></circle>
        <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path>
      </svg>
    </button>
  </header>

  <!-- Settings Panel -->
  {#if showSettings}
    <div class="settings-overlay" on:click|self={() => showSettings = false} in:fade={{ duration: 200 }}>
      <div class="settings-panel" in:fly={{ y: -20, duration: 300 }} out:fade={{ duration: 200 }}>
        <button class="close-settings" on:click={() => showSettings = false}>
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <line x1="18" y1="6" x2="6" y2="18"></line>
            <line x1="6" y1="6" x2="18" y2="18"></line>
          </svg>
        </button>
        
        <div class="settings-grid">
          <!-- Model Selection Section -->
          <div class="settings-section">
            <h3 class="settings-heading">Model Selection</h3>
            <div class="form-group">
              <label class="form-label" for="model-select">AI Model</label>
              <div class="select-wrapper">
                <select id="model-select" class="form-select" bind:value={selectedModel}>
                  <option value="" disabled>Select a model</option>
                  {#each availableModels as model}
                    <option value={model.name}>{model.name}</option>
                  {/each}
                </select>
              </div>
            </div>
  
            <div class="form-group">
              <label class="form-label" for="prompt-select">System Prompt</label>
              <div class="select-wrapper">
                <select id="prompt-select" class="form-select" bind:value={selectedPrompt}>
                  <option value="">Default</option>
                  {#each availablePrompts as prompt}
                    <option value={prompt.id}>{prompt.name}</option>
                  {/each}
                </select>
              </div>
            </div>
          </div>
  
          <!-- Generation Parameters Section -->
          <div class="settings-section">
            <h3 class="settings-heading">Generation Parameters</h3>
            <div class="form-group">
              <div class="slider-container">
                <div class="slider-header">
                  <label for="temperature">Temperature</label>
                  <span class="slider-value">{temperature.toFixed(1)}</span>
                </div>
                <input id="temperature" type="range" min="0" max="2" step="0.1" bind:value={temperature} />
                <div class="range-labels">
                  <span>Precise</span>
                  <span>Creative</span>
                </div>
              </div>
            </div>
            
            <div class="form-group">
              <div class="slider-container">
                <div class="slider-header">
                  <label for="max-tokens">Max Response Length</label>
                  <span class="slider-value">{maxTokens}</span>
                </div>
                <input id="max-tokens" type="range" min="100" max="4000" step="100" bind:value={maxTokens} />
                <div class="range-labels">
                  <span>Short</span>
                  <span>Long</span>
                </div>
              </div>
            </div>
          </div>
          
          <!-- Advanced Features Section -->
          <div class="settings-section">
            <h3 class="settings-heading">Advanced Features</h3>
            
            <div class="form-group">
              <div class="toggle-switch">
                <label for="knowledge-retrieval">Knowledge Retrieval (RAG)</label>
                <label class="toggle">
                  <input type="checkbox" id="knowledge-retrieval" bind:checked={useRAG} />
                  <span class="slider"></span>
                </label>
              </div>
              <p class="feature-description">Enable context retrieval from your documents</p>
            </div>
            
            {#if useRAG}
              <div class="feature-sub-option" in:fly={{ y: -10, duration: 200 }}>
                <label class="form-label">Embedding Model</label>
                <div class="select-wrapper">
                  <select class="form-select" bind:value={selectedEmbedding}>
                    <option value="" disabled>Select embedding model</option>
                    {#each availableEmbeddings as embedding}
                      <option value={embedding.id}>{embedding.name}</option>
                    {/each}
                  </select>
                </div>
              </div>
            {/if}
            
            <div class="form-group">
              <div class="toggle-switch">
                <label for="ai-tools">AI Tools</label>
                <label class="toggle">
                  <input type="checkbox" id="ai-tools" bind:checked={useTools} />
                  <span class="slider"></span>
                </label>
              </div>
              <p class="feature-description">Enable AI to use external tools</p>
            </div>
            
            {#if useTools}
              <div class="feature-sub-option" in:fly={{ y: -10, duration: 200 }}>
                <label class="form-label">Active Tools</label>
                <div class="tools-grid">
                  {#each availableTools as tool}
                    <label class="tool-option">
                      <input 
                        type="checkbox" 
                        value={tool.id}
                        bind:group={selectedTools}
                      />
                      <span class="tool-checkbox"></span>
                      <span class="tool-name">{tool.name}</span>
                    </label>
                  {/each}
                </div>
              </div>
            {/if}
          </div>
        </div>
      </div>
    </div>
  {/if}

  <!-- Chat Messages Container -->
  <div class="messages-container" class:with-settings={showSettings}>
    {#if messages.length === 0}
      <div class="chat-welcome" in:fade={{ duration: 400 }}>
        <div class="welcome-icon">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="40" height="40" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
          </svg>
        </div>
        <h3>Start a conversation</h3>
        <p>Select a model and start chatting with the AI. You can customize behavior using the settings panel.</p>
      </div>
    {:else}
      <div class="chat-thread">
        {#each messages as message, i}
          <div 
            class="message {message.role === 'user' ? 'user-message' : 'model-message'}"
            in:fly={{ y: 20, duration: 300, delay: 100 }}
          >
            {#if message.role === 'user'}
              <div class="message-content user-bubble">
                {message.content}
              </div>
            {:else}
              <div class="message-content model-bubble">
                {@html markedLib ? markedLib.parse(message.content) : simpleMarkdownFormat(message.content)}
              </div>
            {/if}
          </div>
        {/each}

        {#if isLoading}
          <div class="message model-message loading-message" in:fade={{ duration: 200 }}>
            <div class="message-content model-bubble">
              <div class="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        {/if}
      </div>
    {/if}
  </div>

  <!-- Error Message -->
  {#if error}
    <div class="error-alert" in:fly={{ y: 20, duration: 300 }}>
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <circle cx="12" cy="12" r="10"></circle>
        <line x1="12" y1="8" x2="12" y2="12"></line>
        <line x1="12" y1="16" x2="12.01" y2="16"></line>
      </svg>
      <span>{error}</span>
      <button class="error-close" on:click={() => error = ''}>
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <line x1="18" y1="6" x2="6" y2="18"></line>
          <line x1="6" y1="6" x2="18" y2="18"></line>
        </svg>
      </button>
    </div>
  {/if}

  <!-- Chat Input Form -->
  <div class="input-area">
    <form on:submit|preventDefault={sendMessage} class="input-form">
      <div class="input-wrapper">
        <textarea 
          class="message-input"
          bind:value={userInput}
          placeholder={selectedModel ? "Type your message..." : "Select a model to start chatting..."}
          rows="1"
          disabled={isLoading || !selectedModel}
          on:keypress={(e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
              e.preventDefault();
              sendMessage();
            }
          }}
        ></textarea>
        <button 
          type="submit" 
          class="send-button"
          disabled={isLoading || !userInput.trim() || !selectedModel}
          aria-label="Send message"
        >
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <line x1="22" y1="2" x2="11" y2="13"></line>
            <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
          </svg>
        </button>
      </div>
      <div class="input-footer">
        <span class="input-tip">Press <kbd>Enter</kbd> to send, <kbd>Shift</kbd>+<kbd>Enter</kbd> for new line</span>
        <span class="model-indicator">{selectedModel ? `Using: ${selectedModel}` : 'No model selected'}</span>
      </div>
    </form>
  </div>
</div>

<style>
  /* Main layout */
  .chat-layout {
    display: flex;
    flex-direction: column;
    height: 100vh;
    max-width: 1400px;
    margin: 0 auto;
    padding: var(--spacing-4);
    background: var(--surface-0);
    position: relative;
  }
  
  /* Chat header */
  .chat-header {
    position: relative;
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: var(--spacing-4) var(--spacing-6);
    background-color: var(--surface-1);
    border-radius: var(--radius-xl) var(--radius-xl) 0 0;
    border: 1px solid var(--border-light);
    border-bottom: none;
    box-shadow: var(--shadow-sm);
    z-index: 10;
  }
  
  .chat-title {
    font-size: 1.25rem;
    font-weight: 600;
    color: var(--text-primary);
    margin: 0;
  }
  
  .settings-button {
    position: relative;
    z-index: 10;
    background: transparent;
    border: none;
    border-radius: 50%;
    width: 40px;
    height: 40px;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: all 0.2s ease;
    color: #4b5563;
  }
  
  .settings-button:hover {
    background-color: rgba(0, 0, 0, 0.05);
    transform: rotate(30deg);
  }
  
  .settings-button svg {
    width: 20px;
    height: 20px;
  }
  
  /* Settings panel */
  .settings-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: rgba(0, 0, 0, 0.5);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 100;
    padding: 20px;
  }
  
  .settings-panel {
    background-color: white;
    border-radius: 12px;
    box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
    padding: 24px;
    max-width: 1200px;
    width: 100%;
    max-height: 80vh;
    overflow-y: auto;
    position: relative;
  }
  
  .close-settings {
    position: absolute;
    top: 16px;
    right: 16px;
    background: transparent;
    border: none;
    cursor: pointer;
    padding: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #6b7280;
    border-radius: 50%;
    transition: background-color 0.2s;
    z-index: 2;
  }
  
  .close-settings:hover {
    background-color: rgba(0, 0, 0, 0.05);
    color: #1f2937;
  }
  
  .settings-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 32px;
    margin-top: 10px;
  }
  
  .settings-section {
    display: flex;
    flex-direction: column;
    gap: 16px;
  }
  
  .settings-heading {
    font-size: 18px;
    font-weight: 600;
    color: #1f2937;
    margin: 0 0 8px 0;
    padding-bottom: 8px;
    border-bottom: 1px solid #e5e7eb;
  }
  
  /* Form Controls */
  .form-group {
    margin-bottom: 16px;
  }
  
  .form-label {
    display: block;
    font-size: 14px;
    font-weight: 500;
    color: #4b5563;
    margin-bottom: 6px;
  }
  
  /* Select styling */
  .select-wrapper {
    position: relative;
  }
  
  .select-wrapper::after {
    content: '';
    position: absolute;
    right: 14px;
    top: 50%;
    transform: translateY(-50%);
    width: 0;
    height: 0;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 5px solid #6b7280;
    pointer-events: none;
  }
  
  .form-select {
    width: 100%;
    padding: 10px 14px;
    border-radius: 8px;
    border: 1px solid #e5e7eb;
    background-color: white;
    font-size: 14px;
    appearance: none;
    cursor: pointer;
  }
  
  .form-select:focus {
    outline: none;
    border-color: #3b82f6;
    box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.3);
  }
  
  /* Slider styling */
  .slider-container {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }
  
  .slider-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  
  .slider-value {
    font-weight: 600;
    background-color: #f3f4f6;
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 14px;
    color: #3b82f6;
  }
  
  input[type="range"] {
    width: 100%;
    height: 6px;
    -webkit-appearance: none;
    background: linear-gradient(to right, #93c5fd, #3b82f6);
    border-radius: 3px;
    outline: none;
  }
  
  input[type="range"]::-webkit-slider-thumb {
    -webkit-appearance: none;
    width: 16px;
    height: 16px;
    background: #3b82f6;
    border: 2px solid white;
    border-radius: 50%;
    cursor: pointer;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    transition: transform 0.2s;
  }
  
  input[type="range"]::-webkit-slider-thumb:hover {
    transform: scale(1.1);
  }
  
  .range-labels {
    display: flex;
    justify-content: space-between;
    font-size: 12px;
    color: #6b7280;
  }
  
  /* Toggle Switch */
  .toggle-switch {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 4px;
  }
  
  .toggle {
    position: relative;
    display: inline-block;
    width: 44px;
    height: 24px;
  }
  
  .toggle input {
    opacity: 0;
    width: 0;
    height: 0;
  }
  
  .slider {
    position: absolute;
    cursor: pointer;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: #e5e7eb;
    transition: .4s;
    border-radius: 24px;
  }
  
  .slider:before {
    position: absolute;
    content: "";
    height: 18px;
    width: 18px;
    left: 3px;
    bottom: 3px;
    background-color: white;
    transition: .4s;
    border-radius: 50%;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
  }
  
  input:checked + .slider {
    background-color: #3b82f6;
  }
  
  input:checked + .slider:before {
    transform: translateX(20px);
  }
  
  .feature-description {
    font-size: 12px;
    color: #6b7280;
    margin-top: 2px;
  }
  
  .feature-sub-option {
    margin-left: 16px;
    margin-bottom: 16px;
    padding: 12px;
    border-left: 2px solid #93c5fd;
    background-color: #f9fafb;
    border-radius: 8px;
  }
  
  .tools-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
    gap: 8px;
    margin-top: 8px;
  }
  
  .tool-option {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 4px;
    cursor: pointer;
    position: relative;
  }
  
  .tool-option input[type="checkbox"] {
    opacity: 0;
    position: absolute;
  }
  
  .tool-checkbox {
    width: 16px;
    height: 16px;
    border: 2px solid #d1d5db;
    border-radius: 4px;
    position: relative;
    transition: all 0.2s;
    flex-shrink: 0;
  }
  
  .tool-option input[type="checkbox"]:checked + .tool-checkbox {
    background-color: #3b82f6;
    border-color: #3b82f6;
  }
  
  .tool-option input[type="checkbox"]:checked + .tool-checkbox:after {
    content: '';
    position: absolute;
    top: 2px;
    left: 5px;
    width: 4px;
    height: 8px;
    border: solid white;
    border-width: 0 2px 2px 0;
    transform: rotate(45deg);
  }
  
  .tool-name {
    font-size: 14px;
  }
  
  /* Messages area */
  .messages-container {
    display: flex;
    flex-direction: column;
    flex: 1;
    gap: 8px;
    padding: 16px;
    overflow-y: auto;
    border: 1px solid var(--border-light);
    border-radius: 0 0 var(--radius-xl) var(--radius-xl);
    background-color: var(--surface-0);
    box-shadow: var(--shadow-inner);
    height: calc(100vh - 140px);
  }
  
  .messages-container.with-settings {
    border-radius: 0;
  }
  
  .chat-welcome {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    height: 100%;
    min-height: 200px;
    padding: var(--spacing-8);
    color: var(--text-secondary);
  }
  
  .welcome-icon {
    margin-bottom: var(--spacing-4);
    color: var(--primary-300);
    background-color: var(--primary-50);
    padding: var(--spacing-4);
    border-radius: 50%;
  }
  
  .chat-thread {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-4);
  }
  
  /* Modern chat bubbles */
  .message {
    display: flex;
    max-width: 100%;
    margin-bottom: 12px;
  }
  
  .message-content {
    max-width: 75%;
    padding: 12px 16px;
    line-height: 1.5;
    word-wrap: break-word;
    border-radius: 18px;
  }
  
  .user-message {
    justify-content: flex-end;
  }
  
  .model-message {
    justify-content: flex-start;
  }
  
  .user-bubble {
    background-color: #3b82f6; /* Blue */
    color: white;
    border-bottom-right-radius: 4px;
    animation: slideInRight 0.3s ease forwards;
  }
  
  .model-bubble {
    background-color: #f3f4f6; /* Light gray */
    color: #1f2937;
    border-bottom-left-radius: 4px;
    animation: slideInLeft 0.3s ease forwards;
  }
  
  /* Message animations */
  @keyframes slideInRight {
    from {
      opacity: 0;
      transform: translateX(20px);
    }
    to {
      opacity: 1;
      transform: translateX(0);
    }
  }
  
  @keyframes slideInLeft {
    from {
      opacity: 0;
      transform: translateX(-20px);
    }
    to {
      opacity: 1;
      transform: translateX(0);
    }
  }
  
  .model-bubble :global(code) {
    font-family: 'Fira Code', monospace;
    font-size: 0.9em;
    background-color: rgba(0, 0, 0, 0.05);
    padding: 0.1em 0.3em;
    border-radius: var(--radius-sm);
    word-break: break-all;
  }
  
  .model-bubble :global(pre) {
    margin: var(--spacing-3) 0;
    padding: var(--spacing-3);
    border-radius: var(--radius-md);
    background-color: rgba(255, 255, 255, 0.7);
    overflow-x: auto;
  }
  
  .model-bubble :global(pre code) {
    background-color: transparent;
    padding: 0;
    font-size: 0.9em;
  }
  
  .typing-indicator {
    display: flex;
    align-items: center;
    gap: 4px;
    min-height: 24px;
  }
  
  .typing-indicator span {
    display: inline-block;
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background-color: #9ca3af;
    animation: bounce 1.4s infinite ease-in-out both;
  }
  
  .typing-indicator span:nth-child(1) {
    animation-delay: -0.32s;
  }
  
  .typing-indicator span:nth-child(2) {
    animation-delay: -0.16s;
  }
  
  @keyframes bounce {
    0%, 80%, 100% { 
      transform: scale(0);
    } 
    40% { 
      transform: scale(1.0);
    }
  }
  
  /* Error message */
  .error-alert {
    display: flex;
    align-items: center;
    gap: var(--spacing-2);
    margin: var(--spacing-3) 0;
    padding: var(--spacing-3) var(--spacing-4);
    border-radius: var(--radius-lg);
    background-color: var(--error-50);
    border: 1px solid var(--error-200);
    color: var(--error-700);
  }
  
  .error-close {
    margin-left: auto;
    background: none;
    border: none;
    color: var(--error-400);
    cursor: pointer;
    padding: 2px;
    border-radius: var(--radius-sm);
    line-height: 0;
  }
  
  .error-close:hover {
    color: var(--error-600);
    background-color: var(--error-100);
  }
  
  /* Modern input area */
  .input-area {
    display: flex;
    align-items: center;
    padding: 12px 16px;
    background-color: white;
    border-top: 1px solid #e5e7eb;
    border: 1px solid var(--border-light);
    border-radius: var(--radius-xl);
    margin-top: var(--spacing-4);
    background-color: var(--surface-1);
    box-shadow: var(--shadow-md);
    position: sticky;
    bottom: 0;
  }
  
  .input-form {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-2);
    width: 100%;
  }
  
  .input-wrapper {
    display: flex;
    gap: var(--spacing-2);
    position: relative;
    align-items: center;
  }
  
  .message-input {
    flex: 1;
    resize: none;
    padding: 12px 16px;
    border: 1px solid #e5e7eb;
    border-radius: 24px;
    font-size: 14px;
    min-height: 50px;
    max-height: 150px;
    outline: none;
    transition: border-color 0.2s, box-shadow 0.2s;
  }
  
  .message-input:focus {
    border-color: #3b82f6;
    box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.3);
  }
  
  .message-input:disabled {
    background-color: var(--neutral-100);
    cursor: not-allowed;
  }
  
  .send-button {
    margin-left: 8px;
    background-color: #3b82f6;
    color: white;
    border: none;
    border-radius: 50%;
    width: 40px;
    height: 40px;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: background-color 0.2s, transform 0.2s;
  }
  
  .send-button:hover {
    background-color: #2563eb;
    transform: translateY(-2px);
  }
  
  .send-button:disabled {
    background-color: var(--neutral-300);
    cursor: not-allowed;
    transform: none;
  }
  
  .input-footer {
    display: flex;
    justify-content: space-between;
    font-size: 0.75rem;
    color: var(--text-tertiary);
    padding: 0 var(--spacing-2);
  }
  
  .input-tip kbd {
    display: inline-block;
    padding: 0.1em 0.4em;
    font-size: 0.75em;
    line-height: 1;
    color: var(--text-secondary);
    background-color: var(--surface-2);
    border: 1px solid var(--border-light);
    border-radius: var(--radius-sm);
    box-shadow: 0 1px 0 rgba(0,0,0,0.1);
    font-family: sans-serif;
    margin: 0 0.2em;
  }
  
  .model-indicator {
    font-weight: 500;
    color: var(--primary-600);
  }
  
  /* Responsive adjustments */
  @media (max-width: 1024px) {
    .settings-grid {
      grid-template-columns: repeat(2, 1fr);
    }
  }
  
  @media (max-width: 768px) {
    .settings-grid {
      grid-template-columns: 1fr;
    }
    
    .chat-header {
      padding: var(--spacing-3) var(--spacing-4);
    }
    
    .settings-panel {
      padding: 20px;
      max-height: 90vh;
    }
    
    .settings-overlay {
      padding: 10px;
    }
    
    .tools-grid {
      grid-template-columns: 1fr 1fr;
    }
  }
  
  @media (max-width: 480px) {
    .chat-layout {
      padding: var(--spacing-2);
    }
    
    .chat-header {
      padding: var(--spacing-3) var(--spacing-4);
    }
    
    .settings-button {
      width: 36px;
      height: 36px;
    }
    
    .settings-button svg {
      width: 18px;
      height: 18px;
    }
    
    .settings-panel {
      padding: 16px;
      border-radius: 8px;
    }
    
    .close-settings {
      top: 10px;
      right: 10px;
    }
    
    .settings-heading {
      font-size: 16px;
    }
    
    .chat-welcome {
      padding: var(--spacing-4);
    }
    
    .tools-grid {
      grid-template-columns: 1fr;
    }
    
    .toggle-switch {
      flex-wrap: wrap;
    }
  }
</style>