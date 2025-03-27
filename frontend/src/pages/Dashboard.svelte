<script lang="ts">
  import { onMount } from 'svelte';
  import { api } from '../lib/api';
  import { modelsStore, authStore, promptsStore, toolsStore } from '../lib/store';
  import Card from '../components/ui/Card.svelte';

  // Get data from stores  
  $: ollamaModels = $modelsStore;
  $: prompts = $promptsStore;
  $: tools = $toolsStore;
  $: user = $authStore.user;
  
  // State for stats
  let stats = {
    totalModels: 0,
    totalPrompts: 0,
    totalTools: 0,
    totalSize: 0,
  };
  
  // Fetch actual models from Ollama
  async function fetchOllamaModels() {
    try {
      const response = await fetch('http://localhost:11434/api/tags');
      if (response.ok) {
        const data = await response.json();
        if (data.models && Array.isArray(data.models)) {
          // Update stats with actual model count
          stats.totalModels = data.models.length;
          
          // Calculate total size
          let sizeBytes = 0;
          data.models.forEach(model => {
            if (model.size) {
              sizeBytes += model.size;
            }
          });
          stats.totalSize = sizeBytes;
          
          // Update the store with actual models
          modelsStore.set(data.models);
        }
      }
    } catch (error) {
      console.error('Error fetching Ollama models:', error);
    }
  }
  
  // Local placeholder data for demonstration
  const recentActivity = [
    { user: 'Alice', action: 'created a new RAG system', time: '15 minutes ago' },
    { user: 'Bob', action: 'shared a code tool', time: '1 hour ago' },
    { user: 'Charlie', action: 'updated llama model', time: '3 hours ago' },
    { user: 'Diana', action: 'created a new prompt', time: '1 day ago' },
  ];

  // Format size in a readable format
  function formatSize(sizeInBytes) {
    if (!sizeInBytes) return "Unknown size";
    
    const sizeInGB = parseFloat(sizeInBytes) / (1024 * 1024 * 1024);
    return `${sizeInGB.toFixed(2)} GB`;
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

  // Get model type display name
  function getModelType(modelName) {
    if (modelName.includes('7b')) return '7B';
    if (modelName.includes('13b')) return '13B';
    if (modelName.includes('70b')) return '70B';
    return 'LLM';
  }

  // Load data on mount
  onMount(async () => {
    // Load models
    if (ollamaModels.length === 0) {
      try {
        const models = await api.getModels();
        modelsStore.set(models);
      } catch (error) {
        console.error('Failed to load models:', error);
      }
    }
    
    // Load prompts
    if (prompts.length === 0) {
      try {
        const promptsList = await api.getPrompts();
        promptsStore.set(promptsList);
      } catch (error) {
        console.error('Failed to load prompts:', error);
      }
    }
    
    // Load tools
    if (tools.length === 0) {
      try {
        const toolsList = await api.getTools();
        toolsStore.set(toolsList);
      } catch (error) {
        console.error('Failed to load tools:', error);
      }
    }
    
    // Calculate stats
    updateStats();
  });
  
  // Update statistics
  function updateStats() {
    stats.totalModels = ollamaModels.length;
    stats.totalPrompts = prompts.length;
    stats.totalTools = tools.length;
    
    // Calculate total size of all models
    stats.totalSize = ollamaModels.reduce((total, model) => {
      return total + (parseFloat(model.size) || 0);
    }, 0);
  }
  
  // Fetch data on mount
  onMount(async () => {
    await fetchOllamaModels();
  });
  
  // Watch for store changes
  $: {
    if (ollamaModels.length > 0) {
      stats.totalModels = ollamaModels.length;
    }
    stats.totalPrompts = prompts.length;
    stats.totalTools = tools.length;
  }
  
  // Navigation helper
  function navigate(path) {
    window.location.hash = '#/' + path;
  }
</script>

<div class="dashboard-container">
  <!-- Welcome header -->
  <div class="welcome-header">
    <div>
      <h1>Welcome, Workshop Admin!</h1>
      <p>Here's an overview of your workshop resources.</p>
    </div>
  </div>
  
  <!-- Stats cards -->
  <div class="stats-container">
    <div class="stat-card model-stat">
      <div class="stat-icon">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"></path>
          <polyline points="3.27 6.96 12 12.01 20.73 6.96"></polyline>
          <line x1="12" y1="22.08" x2="12" y2="12"></line>
        </svg>
      </div>
      <div class="stat-content">
        <div class="stat-value">{stats.totalModels}</div>
        <div class="stat-label">Models</div>
      </div>
    </div>
    
    <div class="stat-card prompt-stat">
      <div class="stat-icon">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
          <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
        </svg>
      </div>
      <div class="stat-content">
        <div class="stat-value">{stats.totalPrompts}</div>
        <div class="stat-label">Prompts</div>
      </div>
    </div>
    
    <div class="stat-card tool-stat">
      <div class="stat-icon">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"></path>
        </svg>
      </div>
      <div class="stat-content">
        <div class="stat-value">{stats.totalTools}</div>
        <div class="stat-label">Tools</div>
      </div>
    </div>
    
    <div class="stat-card size-stat">
      <div class="stat-icon">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
          <polyline points="17 8 12 3 7 8"></polyline>
          <line x1="12" y1="3" x2="12" y2="15"></line>
        </svg>
      </div>
      <div class="stat-content">
        <div class="stat-value">{formatSize(stats.totalSize)}</div>
        <div class="stat-label">Total Size</div>
      </div>
    </div>
  </div>
  
  <!-- Main dashboard content -->
  <div class="dashboard-grid">
    <!-- Quick Actions -->
    <div class="dashboard-card quick-actions">
      <div class="card-header">
        <h2>Quick Actions</h2>
      </div>
      <div class="card-content">
        <button class="action-button chat-action" on:click={() => navigate('chat')}>
          <div class="action-icon">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
            </svg>
          </div>
          <span>Open Chat Interface</span>
        </button>
        
        <button class="action-button model-action" on:click={() => navigate('models/create')}>
          <div class="action-icon">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"></path>
              <line x1="12" y1="12" x2="12" y2="20"></line>
              <line x1="8" y1="9" x2="16" y2="9"></line>
            </svg>
          </div>
          <span>Create Model</span>
        </button>
        
        <button class="action-button prompt-action" on:click={() => navigate('prompts/create')}>
          <div class="action-icon">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
              <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
            </svg>
          </div>
          <span>Create Prompt</span>
        </button>
        
        <button class="action-button tool-action" on:click={() => navigate('tools/create')}>
          <div class="action-icon">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"></path>
            </svg>
          </div>
          <span>Create Tool</span>
        </button>
        
        <button class="action-button document-action" on:click={() => navigate('documents/upload')}>
          <div class="action-icon">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
              <polyline points="14 2 14 8 20 8"></polyline>
              <line x1="12" y1="18" x2="12" y2="12"></line>
              <line x1="9" y1="15" x2="15" y2="15"></line>
            </svg>
          </div>
          <span>Upload Documents</span>
        </button>
      </div>
    </div>
    
    <!-- Recent Items -->
    <div class="dashboard-card recent-items">
      <div class="card-header">
        <h2>My Recent Items</h2>
      </div>
      <div class="card-content">
        {#if ollamaModels.length === 0 && prompts.length === 0}
          <div class="empty-state">
            <p>No recent items found</p>
            <span>Create your first model or prompt to get started</span>
          </div>
        {:else}
          <div class="items-list">
            {#each ollamaModels.slice(0, 3) as model}
              <div class="recent-item">
                <div class="item-info">
                  <div class="item-badge model-badge">MODEL</div>
                  <div class="item-name">{model.name}</div>
                </div>
              </div>
            {/each}
          </div>
        {/if}
      </div>
    </div>
    
    <!-- Community Activity -->
    <div class="dashboard-card community-activity">
      <div class="card-header">
        <h2>Community Activity</h2>
      </div>
      <div class="card-content">
        <div class="activity-list">
          {#each recentActivity as activity}
            <div class="activity-item">
              <div class="activity-avatar">{activity.user[0]}</div>
              <div class="activity-details">
                <div class="activity-text">
                  <strong>{activity.user}</strong> {activity.action}
                </div>
                <div class="activity-time">{activity.time}</div>
              </div>
            </div>
          {/each}
        </div>
      </div>
    </div>
  </div>
  
  <!-- Models Section -->
  <div class="models-section">
    <div class="section-header">
      <h2>My Models</h2>
      <button class="add-button" on:click={() => navigate('models/create')}>
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="10"></circle>
          <line x1="12" y1="8" x2="12" y2="16"></line>
          <line x1="8" y1="12" x2="16" y2="12"></line>
        </svg>
        <span>Add Model</span>
      </button>
    </div>
    
    <div class="models-grid">
      {#if ollamaModels.length === 0}
        <div class="empty-models">
          <div class="empty-icon">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"></path>
            </svg>
          </div>
          <h3>No Models Found</h3>
          <p>You haven't installed any models yet. Install models through Ollama or create a new model.</p>
          <button class="primary-button" on:click={() => navigate('models/create')}>Create Your First Model</button>
        </div>
      {:else}
        {#each ollamaModels as model}
          <div class="model-card">
            <div class="model-header">
              <div class="model-name">{model.name}</div>
              <div class="model-size">{formatSize(model.size)}</div>
            </div>
            <div class="model-type">
              <div class="model-badge">{getModelType(model.name)}</div>
              {#if model.name.includes('instruct')}
                <div class="model-badge instruct">Instruct</div>
              {/if}
            </div>
            <div class="model-date">Modified: {formatDate(model.modified)}</div>
            <div class="model-actions">
              <button class="model-button" on:click={() => navigate(`chat?model=${model.name}`)}>
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
                </svg>
                <span>Chat</span>
              </button>
              <button class="model-button" on:click={() => navigate(`models/edit/${model.name}`)}>
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
                  <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
                </svg>
                <span>Edit</span>
              </button>
              <button class="model-button" on:click={() => {}}>
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <circle cx="12" cy="12" r="10"></circle>
                  <line x1="12" y1="16" x2="12" y2="12"></line>
                  <line x1="12" y1="8" x2="12.01" y2="8"></line>
                </svg>
                <span>Info</span>
              </button>
            </div>
          </div>
        {/each}
      {/if}
    </div>
  </div>
</div>

<style>
  .dashboard-container {
    padding: 32px;
    max-width: 1400px;
    margin: 0 auto;
  }
  
  /* Welcome Header */
  .welcome-header {
    margin-bottom: 24px;
  }
  
  .welcome-header h1 {
    font-size: 32px;
    font-weight: 700;
    color: #1a202c;
    margin: 0 0 8px 0;
  }
  
  .welcome-header p {
    font-size: 16px;
    color: #4a5568;
    margin: 0;
  }
  
  /* Stats Container */
  .stats-container {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 24px;
    margin-bottom: 32px;
  }
  
  @media (max-width: 1024px) {
    .stats-container {
      grid-template-columns: repeat(2, 1fr);
    }
  }
  
  @media (max-width: 640px) {
    .stats-container {
      grid-template-columns: 1fr;
    }
  }
  
  /* Stat Cards */
  .stat-card {
    display: flex;
    align-items: center;
    padding: 24px;
    border-radius: 12px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05), 0 1px 3px rgba(0, 0, 0, 0.1);
    transition: transform 0.2s, box-shadow 0.2s;
  }
  
  .stat-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 10px 15px rgba(0, 0, 0, 0.1);
  }
  
  .model-stat {
    background: linear-gradient(135deg, #4F46E5, #7C3AED);
    color: white;
  }
  
  .prompt-stat {
    background: linear-gradient(135deg, #0EA5E9, #0284C7);
    color: white;
  }
  
  .tool-stat {
    background: linear-gradient(135deg, #10B981, #059669);
    color: white;
  }
  
  .size-stat {
    background: linear-gradient(135deg, #F97316, #EA580C);
    color: white;
  }
  
  .stat-icon {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 48px;
    height: 48px;
    background-color: rgba(255, 255, 255, 0.2);
    border-radius: 12px;
    margin-right: 16px;
  }
  
  .stat-icon svg {
    width: 24px;
    height: 24px;
    stroke: white;
  }
  
  .stat-content {
    display: flex;
    flex-direction: column;
  }
  
  .stat-value {
    font-size: 28px;
    font-weight: 700;
    line-height: 1.2;
  }
  
  .stat-label {
    font-size: 16px;
    font-weight: 500;
    opacity: 0.9;
  }
  
  /* Dashboard Grid */
  .dashboard-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 24px;
    margin-bottom: 32px;
  }
  
  @media (max-width: 1024px) {
    .dashboard-grid {
      grid-template-columns: repeat(2, 1fr);
    }
    
    .community-activity {
      grid-column: span 2;
    }
  }
  
  @media (max-width: 768px) {
    .dashboard-grid {
      grid-template-columns: 1fr;
    }
    
    .community-activity {
      grid-column: auto;
    }
  }
  
  /* Dashboard Cards */
  .dashboard-card {
    background-color: white;
    border-radius: 12px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05), 0 1px 3px rgba(0, 0, 0, 0.1);
    overflow: hidden;
    height: 100%;
    display: flex;
    flex-direction: column;
    transition: box-shadow 0.2s;
  }
  
  .dashboard-card:hover {
    box-shadow: 0 10px 15px rgba(0, 0, 0, 0.1);
  }
  
  .card-header {
    padding: 16px 20px;
    border-bottom: 1px solid #e2e8f0;
  }
  
  .card-header h2 {
    font-size: 18px;
    font-weight: 600;
    color: #1a202c;
    margin: 0;
  }
  
  .card-content {
    padding: 20px;
    flex-grow: 1;
    display: flex;
    flex-direction: column;
  }
  
  /* Quick Actions */
  .action-button {
    display: flex;
    align-items: center;
    padding: 12px 16px;
    background-color: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    margin-bottom: 12px;
    cursor: pointer;
    transition: all 0.2s;
    font-weight: 500;
  }
  
  .action-button:last-child {
    margin-bottom: 0;
  }
  
  .action-icon {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 36px;
    height: 36px;
    border-radius: 8px;
    margin-right: 12px;
  }
  
  .action-icon svg {
    width: 20px;
    height: 20px;
  }
  
  .chat-action .action-icon {
    background-color: #EEF2FF;
    color: #4F46E5;
  }
  
  .chat-action:hover {
    background-color: #EEF2FF;
    border-color: #C7D2FE;
  }
  
  .model-action .action-icon {
    background-color: #EDE9FE;
    color: #7C3AED;
  }
  
  .model-action:hover {
    background-color: #EDE9FE;
    border-color: #DDD6FE;
  }
  
  .prompt-action .action-icon {
    background-color: #E0F2FE;
    color: #0EA5E9;
  }
  
  .prompt-action:hover {
    background-color: #E0F2FE;
    border-color: #BAE6FD;
  }
  
  .tool-action .action-icon {
    background-color: #DCFCE7;
    color: #10B981;
  }
  
  .tool-action:hover {
    background-color: #DCFCE7;
    border-color: #A7F3D0;
  }
  
  .document-action .action-icon {
    background-color: #FEF3C7;
    color: #F59E0B;
  }
  
  .document-action:hover {
    background-color: #FEF3C7;
    border-color: #FDE68A;
  }
  
  /* Recent Items */
  .items-list {
    display: flex;
    flex-direction: column;
    gap: 12px;
    width: 100%;
  }
  
  .recent-item {
    padding: 12px;
    background-color: #f8fafc;
    border-radius: 8px;
    border-left: 3px solid #4F46E5;
  }
  
  .item-info {
    display: flex;
    align-items: center;
  }
  
  .item-badge {
    font-size: 12px;
    font-weight: 600;
    padding: 4px 8px;
    border-radius: 4px;
    margin-right: 8px;
  }
  
  .model-badge {
    background-color: #EDE9FE;
    color: #7C3AED;
  }
  
  .item-name {
    font-size: 14px;
    font-weight: 500;
    color: #1a202c;
  }
  
  /* Activity items */
  .activity-list {
    display: flex;
    flex-direction: column;
    gap: 12px;
  }
  
  .activity-item {
    display: flex;
    padding: 12px;
    background-color: #f8fafc;
    border-radius: 8px;
  }
  
  .activity-avatar {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 40px;
    height: 40px;
    border-radius: 9999px;
    background-color: #4F46E5;
    color: white;
    font-weight: 600;
    margin-right: 12px;
  }
  
  .activity-details {
    display: flex;
    flex-direction: column;
  }
  
  .activity-text {
    font-size: 14px;
    color: #1a202c;
    margin-bottom: 4px;
  }
  
  .activity-time {
    font-size: 12px;
    color: #64748b;
  }
  
  /* Models section */
  .models-section {
    margin-bottom: 32px;
  }
  
  .section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16px;
  }
  
  .section-header h2 {
    font-size: 24px;
    font-weight: 600;
    color: #1a202c;
    margin: 0;
  }
  
  .add-button {
    display: flex;
    align-items: center;
    padding: 8px 16px;
    background-color: #4F46E5;
    color: white;
    border: none;
    border-radius: 8px;
    font-weight: 500;
    cursor: pointer;
    transition: background-color 0.2s;
  }
  
  .add-button:hover {
    background-color: #4338ca;
  }
  
  .add-button svg {
    width: 16px;
    height: 16px;
    stroke: white;
    margin-right: 8px;
  }
  
  /* Models grid */
  .models-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 24px;
  }
  
  @media (max-width: 640px) {
    .models-grid {
      grid-template-columns: 1fr;
    }
  }
  
  /* Empty state */
  .empty-models {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 48px;
    background-color: white;
    border-radius: 12px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05), 0 1px 3px rgba(0, 0, 0, 0.1);
    text-align: center;
    grid-column: 1 / -1;
  }
  
  .empty-icon {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 64px;
    height: 64px;
    background-color: #f1f5f9;
    border-radius: 9999px;
    margin-bottom: 16px;
  }
  
  .empty-icon svg {
    width: 32px;
    height: 32px;
    stroke: #64748b;
  }
  
  .empty-models h3 {
    font-size: 18px;
    font-weight: 600;
    color: #1a202c;
    margin: 0 0 8px 0;
  }
  
  .empty-models p {
    font-size: 14px;
    color: #64748b;
    margin: 0 0 24px 0;
    max-width: 400px;
  }
  
  .primary-button {
    padding: 8px 16px;
    background-color: #4F46E5;
    color: white;
    border: none;
    border-radius: 8px;
    font-weight: 500;
    cursor: pointer;
    transition: background-color 0.2s;
  }
  
  .primary-button:hover {
    background-color: #4338ca;
  }
  
  /* Model cards */
  .model-card {
    background-color: white;
    border-radius: 12px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05), 0 1px 3px rgba(0, 0, 0, 0.1);
    padding: 20px;
    display: flex;
    flex-direction: column;
    transition: transform 0.2s, box-shadow 0.2s;
  }
  
  .model-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 10px 15px rgba(0, 0, 0, 0.1);
  }
  
  .model-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
  }
  
  .model-name {
    font-size: 16px;
    font-weight: 600;
    color: #1a202c;
    display: -webkit-box;
    -webkit-line-clamp: 1;
    -webkit-box-orient: vertical;
    overflow: hidden;
  }
  
  .model-size {
    padding: 4px 8px;
    background-color: #f1f5f9;
    border-radius: 4px;
    font-size: 12px;
    font-weight: 500;
    color: #64748b;
  }
  
  .model-type {
    display: flex;
    gap: 8px;
    margin-bottom: 12px;
  }
  
  .model-badge {
    padding: 4px 8px;
    background-color: #EDE9FE;
    border-radius: 4px;
    font-size: 12px;
    font-weight: 500;
    color: #7C3AED;
  }
  
  .model-badge.instruct {
    background-color: #E0F2FE;
    color: #0EA5E9;
  }
  
  .model-date {
    font-size: 12px;
    color: #64748b;
    margin-bottom: 16px;
  }
  
  .model-actions {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 8px;
    margin-top: auto;
  }
  
  .model-button {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 8px;
    background-color: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    transition: all 0.2s;
    cursor: pointer;
  }
  
  .model-button:hover {
    background-color: #f1f5f9;
    border-color: #cbd5e1;
  }
  
  .model-button svg {
    width: 16px;
    height: 16px;
    stroke: #64748b;
    margin-bottom: 4px;
  }
  
  .model-button span {
    font-size: 12px;
    font-weight: 500;
    color: #1a202c;
  }
  
  /* Empty state */
  .empty-state {
    text-align: center;
    padding: 24px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
  }
  
  .empty-state p {
    font-size: 14px;
    font-weight: 500;
    color: #1a202c;
    margin: 0 0 4px 0;
  }
  
  .empty-state span {
    font-size: 12px;
    color: #64748b;
  }
</style>