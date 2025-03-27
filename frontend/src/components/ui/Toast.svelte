<script lang="ts">
  import { fade } from 'svelte/transition';
  import { createEventDispatcher } from 'svelte';
  
  export let message = '';
  export let type = 'info'; // info, success, error, warning
  export let duration = 3000; // in milliseconds
  export let showClose = true;
  
  const dispatch = createEventDispatcher();
  
  // Auto-close toast after duration
  let timeout;
  
  $: if (message && duration > 0) {
    clearTimeout(timeout);
    timeout = setTimeout(() => {
      close();
    }, duration);
  }
  
  function close() {
    clearTimeout(timeout);
    dispatch('close');
  }
</script>

{#if message}
  <div 
    class="toast-notification {type}"
    transition:fade={{ duration: 200 }}
    role="alert"
  >
    <div class="toast-icon">
      {#if type === 'success'}
        <span>✓</span>
      {:else if type === 'error'}
        <span>✕</span>
      {:else if type === 'warning'}
        <span>⚠</span>
      {:else}
        <span>ℹ</span>
      {/if}
    </div>
    
    <div class="toast-content">
      {message}
    </div>
    
    {#if showClose}
      <button
        class="toast-close"
        on:click={close}
        aria-label="Close notification"
      >
        ✕
      </button>
    {/if}
  </div>
{/if}

<style>
  .toast-notification {
    position: fixed;
    bottom: 2rem;
    right: 2rem;
    display: flex;
    align-items: center;
    padding: 0.75rem 1rem;
    border-radius: var(--radius-md);
    box-shadow: var(--shadow-lg);
    color: white;
    min-width: 18rem;
    max-width: 24rem;
    z-index: 9999;
  }
  
  .toast-notification.info {
    background-color: var(--info-600);
  }
  
  .toast-notification.success {
    background-color: var(--success-600);
  }
  
  .toast-notification.error {
    background-color: var(--error-600);
  }
  
  .toast-notification.warning {
    background-color: var(--warning-600);
  }
  
  .toast-icon {
    margin-right: 0.75rem;
    font-size: 1.25rem;
    display: flex;
    align-items: center;
    justify-content: center;
  }
  
  .toast-content {
    flex: 1;
    font-size: 0.875rem;
  }
  
  .toast-close {
    margin-left: 0.75rem;
    background: none;
    border: none;
    color: rgba(255, 255, 255, 0.7);
    cursor: pointer;
    font-size: 1rem;
    padding: 0;
    display: flex;
    align-items: center;
    justify-content: center;
  }
  
  .toast-close:hover {
    color: white;
  }
</style>
