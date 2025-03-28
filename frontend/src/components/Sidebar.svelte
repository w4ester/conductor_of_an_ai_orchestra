<script>
import { createEventDispatcher } from 'svelte';
import { api } from '../lib/api';
import { authStore, toolsStore } from '../lib/store';
import { slide } from 'svelte/transition';

// Define menu items with SVG icons instead of emojis
const menuItems = [
  { name: 'Dashboard', path: '/', icon: 'M4 5a1 1 0 011-1h14a1 1 0 011 1v2a1 1 0 01-1 1H5a1 1 0 01-1-1V5zm0 8a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H5a1 1 0 01-1-1v-6zm10 0a1 1 0 011-1h4a1 1 0 011 1v6a1 1 0 01-1 1h-4a1 1 0 01-1-1v-6z' },
  { name: 'Chat', path: '/chat', icon: 'M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z' },
  { name: 'Models', path: '/models/create', icon: 'M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z' },
  { name: 'Prompts', path: '/prompts', icon: 'M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z' },
  { name: 'Tools', path: '/tools', icon: 'M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z M15 12a3 3 0 11-6 0 3 3 0 016 0z' },
  { name: 'Documents', path: '/documents', icon: 'M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z' },
  { name: 'RAG', path: '/rag', icon: 'M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z' },
  { name: 'Community', path: '/community', icon: 'M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z' },
  { name: 'Settings', path: '/settings', icon: 'M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z M15 12a3 3 0 11-6 0 3 3 0 016 0z' },
];

// Setup for navigation
export let currentPath = '/';
const dispatch = createEventDispatcher();

// Get user from store
$: user = $authStore.user;

// State for mobile sidebar
let isMobileSidebarOpen = false;

// Preload data when needed
async function preloadData(path) {
  // Preload the Tools data when navigating to the Tools page
  if (path === '/tools') {
    try {
      console.log("Preloading tools data...");
      const response = await api.getTools();
      toolsStore.set(response.items || []);
    } catch (error) {
      console.error("Failed to preload tools data:", error);
    }
  }
}

async function navigate(path) {
  // Preload data for destination before navigation
  await preloadData(path);
  
  // Update current path
  currentPath = path;
  dispatch('navigate', { path });
  
  // Close sidebar on mobile after navigation
  if (window.innerWidth < 768) {
    isMobileSidebarOpen = false;
  }
}

function logout() {
  api.clearToken();
  authStore.update(state => ({
    ...state,
    isAuthenticated: false,
    user: null,
    error: null
  }));
  
  dispatch('logout');
}

function toggleMobileSidebar() {
  isMobileSidebarOpen = !isMobileSidebarOpen;
}
</script>

<!-- Mobile hamburger button - only visible on small screens -->
<button 
  class="md:hidden fixed top-4 left-4 z-50 rounded-full w-10 h-10 flex items-center justify-center bg-primary-600 text-white shadow-lg"
  on:click={toggleMobileSidebar}
  aria-label="Toggle menu"
>
  <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
    {#if isMobileSidebarOpen}
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
    {:else}
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
    {/if}
  </svg>
</button>

<!-- Sidebar - conditionally shown on mobile -->
<aside 
  class="sidebar {isMobileSidebarOpen ? 'mobile-open' : 'mobile-closed'}"
  class:mobile-open={isMobileSidebarOpen}
>
  <div class="sidebar-header">
    <h1>AI Workshop</h1>
    <!-- Close button - only visible on small screens -->
    <button 
      class="md:hidden close-button"
      on:click={toggleMobileSidebar}
      aria-label="Close menu"
    >
      <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
      </svg>
    </button>
  </div>

  <nav class="sidebar-nav">
    <ul>
      {#each menuItems as item}
        <li>
          <button 
            on:click={() => navigate(item.path)}
            class={currentPath.startsWith(item.path) ? 'nav-item active' : 'nav-item'}
            aria-current={currentPath.startsWith(item.path) ? 'page' : undefined}
          >
            <span class="icon">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d={item.icon} />
              </svg>
            </span>
            <span class="nav-text">{item.name}</span>
            {#if currentPath.startsWith(item.path)}
              <span class="active-indicator"></span>
            {/if}
          </button>
        </li>
      {/each}
    </ul>
  </nav>

  <div class="user-footer">
    <div class="user-container">
      <div class="user-info">
        <div class="user-avatar">
          {user?.username?.[0]?.toUpperCase() || 'U'}
        </div>
        <div class="user-details">
          <p class="user-name">{user?.full_name || user?.username || 'User'}</p>
          <p class="user-role">{user?.is_admin ? 'Workshop Admin' : 'Attendee'}</p>
        </div>
      </div>
      <button class="logout-button" on:click={logout}>
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
        </svg>
        Logout
      </button>
    </div>
  </div>
</aside>

<!-- Overlay for mobile - only shown when sidebar is open -->
{#if isMobileSidebarOpen}
  <div 
    class="md:hidden fixed inset-0 bg-black bg-opacity-50 z-40"
    on:click={toggleMobileSidebar}
    transition:slide
  ></div>
{/if}

<style>
.sidebar {
  width: 250px;
  height: 100vh;
  background: #1a202c; /* Dark background for strong contrast */
  color: #f8fafc; /* Light text color for contrast */
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  position: relative;
  z-index: 45;
  transition: transform 0.3s ease;
  box-shadow: 0 0 20px rgba(0, 0, 0, 0.2);
}

.sidebar-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  background-color: #0f172a; /* Slightly darker header */
}

.sidebar h1 {
  color: #f8fafc;
  font-size: 1.3rem;
  font-weight: 700;
  margin: 0;
  letter-spacing: 0.5px;
}

.close-button {
  background: transparent;
  border: none;
  color: #f8fafc;
  cursor: pointer;
  padding: 8px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.close-button:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

.sidebar-nav {
  padding: 16px 0;
  flex: 1;
}

.sidebar ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.sidebar li {
  margin-bottom: 2px;
}

.nav-item {
  position: relative;
  display: flex;
  align-items: center;
  width: 100%;
  padding: 12px 20px;
  text-align: left;
  border: none;
  background: transparent;
  color: #e2e8f0; /* Light color for text */
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.2s ease;
  border-radius: 0;
  font-weight: 500;
}

.nav-item:hover {
  background-color: rgba(255, 255, 255, 0.1);
  color: #ffffff;
}

.nav-item.active {
  background-color: rgba(59, 130, 246, 0.2); /* Blue highlight for active item */
  color: #ffffff;
  font-weight: 600;
}

.active-indicator {
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 4px;
  background: #3b82f6; /* Blue indicator */
  border-radius: 0 4px 4px 0;
}

.icon {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 12px;
  color: #e2e8f0;
}

.nav-text {
  flex: 1;
}

.user-footer {
  margin-top: auto;
  padding: 16px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  background-color: #0f172a; /* Slightly darker footer */
}

.user-container {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.user-info {
  display: flex;
  align-items: center;
}

.user-avatar {
  width: 40px;
  height: 40px;
  background: #3b82f6;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: bold;
  font-size: 1.125rem;
  box-shadow: 0 3px 6px rgba(0, 0, 0, 0.2);
}
  
.user-details {
  margin-left: 12px;
  overflow: hidden;
}
  
.user-name {
  font-size: 0.95rem;
  font-weight: 600;
  color: #f8fafc;
  margin: 0 0 2px 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
  
.user-role {
  font-size: 0.75rem;
  color: #cbd5e1;
  margin: 0;
}
  
.logout-button {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  padding: 10px;
  background-color: rgba(239, 68, 68, 0.1); /* Subtle red background */
  border-radius: 8px;
  font-size: 0.9rem;
  font-weight: 600;
  color: #ef4444; /* Red text for logout */
  border: 1px solid rgba(239, 68, 68, 0.2);
  cursor: pointer;
  transition: all 0.2s ease;
}
  
.logout-button:hover {
  background-color: rgba(239, 68, 68, 0.2);
}
  
/* Mobile styles */
@media (max-width: 768px) {
  .sidebar {
    position: fixed;
    top: 0;
    left: 0;
  }
    
  .mobile-closed {
    transform: translateX(-100%);
  }
    
  .mobile-open {
    transform: translateX(0);
  }
}
</style>