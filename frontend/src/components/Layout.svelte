<script lang="ts">
  import { onMount } from 'svelte';
  import Sidebar from './Sidebar.svelte';
  import Toast from './ui/Toast.svelte';
  
  export let currentPath = '/';
  
  // Toast state
  let toastMessage = '';
  let toastType = 'info';
  let toastDuration = 3000;
  
  function handleNavigate(event: CustomEvent) {
    // Ensure path is clean with only one leading slash
    let path = event.detail.path;
    if (path.startsWith('/')) {
      path = path.substring(1);
    }
    
    // Store the cleaned path and update hash
    currentPath = '/' + path;
    window.location.hash = '#/' + path;  // Always use a single hash format
  }
  
  // Show toast notification
  export function showToast(message: string, type: 'info' | 'success' | 'error' | 'warning' = 'info', duration: number = 3000) {
    toastMessage = message;
    toastType = type;
    toastDuration = duration;
  }
  
  // Close toast
  function closeToast() {
    toastMessage = '';
  }
  
  // Handle hash-based navigation
  onMount(() => {
    // Clean and set initial path from hash 
    if (window.location.hash) {
      // Handle hashes in the format #/path or just #path
      let path = window.location.hash.substring(1);
      
      // Remove any leading slash to normalize
      if (path.startsWith('/')) {
        path = path.substring(1);
      }
      
      // Now prepend a single slash
      currentPath = '/' + path;
    }
    
    // Listen for hash changes
    const handleHashChange = () => {
      let path = window.location.hash.substring(1) || '/';
      
      // Remove any leading slash to normalize
      if (path.startsWith('/')) {
        path = path.substring(1);
      }
      
      // Now prepend a single slash
      currentPath = '/' + path;
    };
    
    window.addEventListener('hashchange', handleHashChange);
    
    return () => {
      window.removeEventListener('hashchange', handleHashChange);
    };
  });
</script>

<div class="layout">
  <Sidebar {currentPath} on:navigate={handleNavigate} on:logout />
  
  <main class="main-content">
    <slot></slot>
  </main>
  
  <Toast 
    message={toastMessage} 
    type={toastType} 
    duration={toastDuration}
    on:close={closeToast}
  />
</div>

<style>
  .layout {
    display: flex;
    width: 100%;
    height: 100vh;
    overflow: hidden;
    background-color: var(--surface-0);
  }
  
  .main-content {
    flex: 1;
    overflow-y: auto;
    position: relative;
    background-color: var(--surface-0);
    color: var(--text-primary);
  }
  
  /* Mobile styles */
  @media (max-width: 768px) {
    .main-content {
      width: 100%;
    }
  }
</style>
