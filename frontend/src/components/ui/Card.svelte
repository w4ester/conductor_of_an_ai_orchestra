<script lang="ts">
  export let title = null;
  export let subtitle = null;
  export let headerAction = null;
  export let padding = true;
  export let hover = false;
  export let bordered = true;
</script>

<div class="card" class:hover class:bordered>
  {#if title || headerAction}
    <header class="card-header">
      <div>
        {#if title}
          <h3 class="card-title">{title}</h3>
        {/if}
        
        {#if subtitle}
          <p class="card-subtitle">{subtitle}</p>
        {/if}
      </div>
      
      {#if headerAction}
        <div class="card-action">
          <slot name="header-action"></slot>
        </div>
      {/if}
    </header>
  {/if}
  
  <div class="card-body" class:padding>
    <slot></slot>
  </div>
  
  <slot name="footer"></slot>
</div>

<style>
  .card {
    background-color: var(--surface-2);
    border-radius: var(--radius-lg);
    overflow: hidden;
    height: 100%;
    display: flex;
    flex-direction: column;
    box-shadow: var(--shadow-md);
    transition: transform var(--transition-fast) var(--easing-standard), 
                box-shadow var(--transition-fast) var(--easing-standard);
  }
  
  .card.hover:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow-lg);
  }
  
  .card.bordered {
    border: 1px solid var(--border-light);
  }
  
  .card-header {
    padding: var(--spacing-4);
    background-color: var(--surface-3);
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid var(--border-light);
  }
  
  .card-title {
    font-size: 1rem;
    font-weight: 600;
    color: var(--text-primary);
    margin: 0;
  }
  
  .card-subtitle {
    font-size: 0.875rem;
    color: var(--text-secondary);
    margin: 0.25rem 0 0 0;
  }
  
  .card-body {
    flex: 1;
  }
  
  .card-body.padding {
    padding: var(--spacing-4);
  }
</style>
