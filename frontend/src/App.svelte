<script lang="ts">
  import { onMount } from 'svelte';
  import { get } from 'svelte/store';
  // Remove the direct import of highlight.js CSS
  import Layout from './components/Layout.svelte';
  import Dashboard from './pages/Dashboard.svelte';
  import Login from './pages/Login.svelte';
  import ModelEditor from './pages/ModelEditor.svelte';
  import PromptsPage from './pages/PromptsPage.svelte';
  import PromptEditor from './pages/PromptEditor.svelte';
  import ToolsPage from './pages/ToolsPage.svelte';
  import ToolEditor from './pages/ToolEditor.svelte';
  import DocumentsPage from './pages/DocumentsPage.svelte';
  import DocumentUpload from './pages/DocumentUpload.svelte';
  import VectorDbsPage from './pages/VectorDbsPage.svelte';
  import VectorDbConfig from './pages/VectorDbConfig.svelte';
  import EmbeddingsPage from './pages/EmbeddingsPage.svelte';
  import CreateEmbedding from './pages/CreateEmbedding.svelte';
  import ChatPage from './pages/ChatPage.svelte';
  import DocumentEditor from './pages/DocumentEditor.svelte';
  import { authStore, modelsStore, promptsStore, toolsStore, documentsStore,
           vectorDbsStore, embeddingsStore, embeddingModelsStore } from './lib/store';
  import { api } from './lib/api';

  // Local state for navigation
  let currentPath = '/';
  let loading = true;
  
  // Pages for navigation
  let modelToEdit = '';
  
  // Route parameters and props
  let routeProps = {};
  
  // Routes configuration
  let promptToEdit = '';
  let toolToEdit = '';
  let vectorDbToEdit = '';
  
  function cleanPath(path) {
    // Extract just the part after the hash if there's one
    // and ensure we don't have duplicate path components
    if (path.includes('#')) {
      path = path.split('#').pop();
    }
    
    // Remove any leading slash to normalize
    if (path.startsWith('/')) {
      path = path.substring(1);
    }
    
    // Now prepend a single slash
    return '/' + path;
  }
  
  function getBasePath(path) {
    // Extract the base route without ID parameters
    const parts = cleanPath(path).split('/');
    
    // Handle edit routes with IDs
    if (parts.length >= 3 && parts[2] === 'edit' && parts.length > 3) {
      return '/' + parts[1] + '/' + parts[2];
    }
    
    // Handle normal routes with up to 2 segments
    if (parts.length <= 3) {
      return cleanPath(path);
    }
    
    return '/' + parts[1] + '/' + parts[2];
  }
  
  const routes = {
    '/': { component: Dashboard },
    '/models': { component: ModelEditor, props: { isEdit: false } }, // Direct to model creation
    '/models/create': { component: ModelEditor, props: { isEdit: false } },
    '/models/edit': { component: ModelEditor, props: { isEdit: true } },
    '/prompts': { component: PromptsPage },
    '/prompts/create': { component: PromptEditor, props: { isEdit: false } },
    '/prompts/edit': { component: PromptEditor, props: { isEdit: true } },
    '/tools': { component: ToolsPage },
    '/tools/create': { component: ToolEditor, props: { isEdit: false } },
    '/tools/edit': { component: ToolEditor, props: { isEdit: true } },
    '/documents': { component: DocumentsPage },
    '/documents/upload': { component: DocumentUpload },
    '/documents/create': { component: DocumentEditor, props: { isEdit: false } },
    '/documents/edit': { component: DocumentEditor, props: { isEdit: true } },
    '/documents/view': { component: DocumentEditor, props: { isEdit: true, readOnly: true } }, // For view, we'll use DocumentEditor in read-only mode
    '/vector-dbs': { component: VectorDbsPage },
    '/vector-dbs/create': { component: VectorDbConfig, props: { isEdit: false } },
    '/vector-dbs/edit': { component: VectorDbConfig, props: { isEdit: true } },
    '/embeddings': { component: EmbeddingsPage },
    '/embeddings/create': { component: CreateEmbedding },
    '/chat': { component: ChatPage }, // Chat page
    '/rag': { component: Dashboard },
    '/community': { component: Dashboard },
    '/settings': { component: Dashboard }
  };
  
  // Computed pages object
  $: pages = Object.keys(routes).reduce((acc, path) => {
    acc[path] = routes[path].component;
    return acc;
  }, {});
  
  function handleLogin(event) {
    // Auth state is already updated in the Login component
    currentPath = '/';
    loadModels();
  }
  
  async function loadModels() {
    try {
      const models = await api.getModels();
      modelsStore.set(models);
    } catch (error) {
      console.error('Failed to load models:', error);
    }
  }
  
  // Extract ID from path for edit routes
  function getIdFromPath(path, routePrefix) {
    if (path.startsWith(routePrefix)) {
      return path.substring(routePrefix.length);
    }
    return '';
  }
  
  // Check if user is already logged in
  onMount(async () => {
    // No need to load highlight.js CSS as it's already in index.html
    
    const token = localStorage.getItem('auth_token');
    
    if (token) {
      // If token exists, try to get the current user
      try {
        api.setToken(token);
        const user = await api.getCurrentUser();
        
        // Update auth store if successful
        authStore.update(state => ({
          ...state,
          isAuthenticated: true,
          user,
          loading: false
        }));
        
        // Load models
        loadModels();
      } catch (error) {
        // If getting user fails, clear token
        api.clearToken();
        authStore.update(state => ({
          ...state,
          loading: false
        }));
      }
    } else {
      // No token, just set loading to false
      authStore.update(state => ({
        ...state,
        loading: false
      }));
    }
    
    loading = false;
  });
  
  // Subscribe to auth store
  $: isAuthenticated = $authStore.isAuthenticated;
  $: user = $authStore.user;
  
  // Get the base path for component selection
  $: basePath = getBasePath(currentPath);
  
  // Extract IDs from the current path for edit routes
  $: modelId = currentPath.startsWith('/models/edit/') ? getIdFromPath(currentPath, '/models/edit/') : '';
  $: promptId = currentPath.startsWith('/prompts/edit/') ? getIdFromPath(currentPath, '/prompts/edit/') : '';
  $: toolId = currentPath.startsWith('/tools/edit/') ? getIdFromPath(currentPath, '/tools/edit/') : '';
  $: dbId = currentPath.startsWith('/vector-dbs/edit/') ? getIdFromPath(currentPath, '/vector-dbs/edit/') : '';
  $: documentId = currentPath.startsWith('/documents/edit/') ? getIdFromPath(currentPath, '/documents/edit/') : 
                 currentPath.startsWith('/documents/view/') ? getIdFromPath(currentPath, '/documents/view/') : '';
</script>

{#if loading}
  <div class="loading-screen">
    <div class="loading-spinner"></div>
    <p>Loading the Ollama Workshop Platform...</p>
  </div>
{:else if isAuthenticated}
  <Layout bind:currentPath on:logout={() => isAuthenticated = false}>
    {#if pages[basePath]}
      <svelte:component 
        this={pages[basePath]} 
        {...(routes[basePath]?.props || {})}
        modelName={modelId}
        promptId={promptId}
        toolId={toolId}
        dbId={dbId}
        documentId={documentId}
        readOnly={basePath === '/documents/view'}
      />
    {:else}
      <div class="not-found">
        <div class="empty-state">
          <div class="empty-icon">🔍</div>
          <h2 class="h2">Page Not Found</h2>
          <p>The page you are looking for does not exist.</p>
          <button class="btn btn-primary mt-4" on:click={() => { currentPath = '/'; window.location.hash = '#/'; }}>
            Go to Dashboard
          </button>
        </div>
      </div>
    {/if}
  </Layout>
{:else}
  <Login on:login={handleLogin} />
{/if}

<style>
  .loading-screen {
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    height: 100vh;
    background-color: var(--surface-1);
    color: var(--text-primary);
  }
  
  .loading-spinner {
    width: 3rem;
    height: 3rem;
    border: 3px solid rgba(59, 130, 246, 0.3);
    border-radius: 50%;
    border-top-color: var(--primary-500);
    animation: spin 1s linear infinite;
    margin-bottom: var(--spacing-4);
  }
  
  @keyframes spin {
    to { transform: rotate(360deg); }
  }
  
  .not-found {
    display: flex;
    justify-content: center;
    align-items: center;
    height: calc(100vh - 80px);
  }
</style>
