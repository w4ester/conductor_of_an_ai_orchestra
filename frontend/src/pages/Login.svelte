<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import { api } from '../lib/api';
  import { authStore } from '../lib/store';
  
  const dispatch = createEventDispatcher();
  
  let username = '';
  let password = '';
  let rememberMe = false;
  let errorMessage = '';
  let loading = false;
  
  async function login() {
    if (!username || !password) {
      errorMessage = 'Please enter both username and password.';
      return;
    }
    
    loading = true;
    errorMessage = '';
    
    try {
      // Make the actual API call
      const user = await api.login({
        username,
        password
      });
      
      // Update the auth store
      authStore.update(state => ({
        ...state,
        isAuthenticated: true,
        user,
        error: null
      }));
      
      // Dispatch a login event that the parent component can listen for
      dispatch('login', { user });
      
    } catch (error) {
      console.error('Login error:', error);
      errorMessage = error.message || 'Login failed. Please check your credentials.';
    } finally {
      loading = false;
    }
  }
  
  // For development/demo purposes, provide quick login options
  function loginAsAdmin() {
    username = 'admin';
    password = 'admin';
    login();
  }
  
  function loginAsUser() {
    username = 'workshopuser';
    password = 'password';
    login();
  }
</script>

<div class="login-container">
  <div class="login-card">
    <div class="login-header">
      <h1>AI Conductor Workshop</h1>
      <p>Sign in to your account</p>
    </div>
    
    {#if errorMessage}
      <div class="alert alert-error" role="alert">
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="12" cy="12" r="10"></circle>
          <line x1="12" y1="8" x2="12" y2="12"></line>
          <line x1="12" y1="16" x2="12.01" y2="16"></line>
        </svg>
        <span>{errorMessage}</span>
      </div>
    {/if}
    
    <form on:submit|preventDefault={login} class="login-form">
      <div class="form-group">
        <label for="username" class="form-label">Username</label>
        <input 
          type="text" 
          id="username" 
          bind:value={username}
          class="form-input"
          placeholder="Username"
          autocomplete="username"
        />
      </div>
      
      <div class="form-group">
        <label for="password" class="form-label">Password</label>
        <input 
          type="password" 
          id="password" 
          bind:value={password}
          class="form-input"
          placeholder="••••••••"
          autocomplete="current-password"
        />
      </div>
      
      <div class="flex-between">
        <label class="remember-me">
          <input 
            type="checkbox" 
            bind:checked={rememberMe}
          />
          <span>Remember me</span>
        </label>
        
        <a href="#" class="forgot-password">
          Forgot password?
        </a>
      </div>
      
      <button 
        type="submit" 
        class="btn btn-primary w-full"
        disabled={loading}
      >
        {#if loading}
          <span class="loading-spinner"></span>
          <span>Signing in...</span>
        {:else}
          Sign in
        {/if}
      </button>
    </form>
    
    <div class="separator">
      <span>Quick login options</span>
    </div>
    
    <div class="alt-login-buttons">
      <button class="alt-login-btn workshop-btn" on:click={loginAsAdmin}>
        <span>Admin</span>
      </button>
      <button class="alt-login-btn guest-btn" on:click={loginAsUser}>
        <span>Workshop User</span>
      </button>
    </div>
    
    <p class="signup-link">
      Default credentials: 
      <br>
      Admin: admin / admin
      <br>
      User: workshopuser / password
    </p>
  </div>
</div>

<style>
  .login-container {
    display: flex;
    min-height: 100vh;
    align-items: center;
    justify-content: center;
    padding: var(--spacing-6);
    background: linear-gradient(135deg, var(--primary-600), var(--primary-800));
    position: relative;
    overflow: hidden;
  }

  /* Add some decorative elements */
  .login-container::before {
    content: '';
    position: absolute;
    top: -50px;
    right: -50px;
    width: 300px;
    height: 300px;
    border-radius: 50%;
    background-color: rgba(255, 255, 255, 0.1);
    z-index: 0;
  }

  .login-container::after {
    content: '';
    position: absolute;
    bottom: -100px;
    left: -100px;
    width: 500px;
    height: 500px;
    border-radius: 50%;
    background-color: rgba(255, 255, 255, 0.05);
    z-index: 0;
  }

  .login-card {
    width: 100%;
    max-width: 420px;
    background-color: white;
    border-radius: 16px;
    box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
    padding: 32px;
    border: 1px solid rgba(255, 255, 255, 0.2);
    position: relative;
    z-index: 1;
    transition: transform 0.3s ease, box-shadow 0.3s ease;
  }

  .login-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
  }

  .login-header {
    text-align: center;
    margin-bottom: 32px;
  }

  .login-header h1 {
    font-size: 2rem;
    font-weight: 800;
    color: #1a202c;
    margin-bottom: 8px;
  }

  .login-header p {
    color: #4b5563;
    font-size: 1rem;
    font-weight: 500;
  }
  
  .login-form {
    margin-bottom: 24px;
  }
  
  .form-group {
    margin-bottom: 24px;
  }

  .form-label {
    display: block;
    margin-bottom: 8px;
    font-size: 0.9rem;
    font-weight: 600;
    color: #374151;
  }
  
  .flex-between {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 24px;
  }
  
  .form-input {
    width: 100%;
    padding: 12px 16px;
    background-color: #f9fafb;
    border: 2px solid #e5e7eb;
    border-radius: 8px;
    color: #1f2937;
    font-size: 1rem;
    transition: all 0.2s ease;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
  }

  .form-input:hover {
    border-color: #d1d5db;
  }

  .form-input:focus {
    outline: none;
    border-color: #3b82f6;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.3);
    background-color: white;
  }
  
  .remember-me {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 0.9rem;
    color: #4b5563;
    cursor: pointer;
  }
  
  .remember-me input[type="checkbox"] {
    appearance: none;
    width: 18px;
    height: 18px;
    border: 2px solid #d1d5db;
    background-color: white;
    border-radius: 4px;
    display: grid;
    place-content: center;
    transition: all 0.2s ease;
  }

  .remember-me input[type="checkbox"]:checked {
    background-color: #3b82f6;
    border-color: #3b82f6;
  }

  .remember-me input[type="checkbox"]:checked::before {
    content: "";
    width: 0.65em;
    height: 0.65em;
    transform: scale(1);
    transition: 120ms transform ease-in-out;
    box-shadow: inset 1em 1em white;
    transform-origin: center;
    clip-path: polygon(14% 44%, 0 65%, 50% 100%, 100% 16%, 80% 0%, 43% 62%);
  }
  
  .forgot-password {
    font-size: 0.9rem;
    font-weight: 500;
    color: #3b82f6;
    text-decoration: none;
    transition: color 0.2s ease;
  }
  
  .forgot-password:hover {
    color: #2563eb;
    text-decoration: underline;
  }
  
  .btn-primary {
    background: #3b82f6;
    color: white;
    font-weight: 600;
    padding: 12px;
    border-radius: 8px;
    width: 100%;
    border: none;
    cursor: pointer;
    transition: all 0.2s ease;
    box-shadow: 0 4px 6px rgba(59, 130, 246, 0.25);
    font-size: 1rem;
    text-align: center;
  }

  .btn-primary:hover {
    background: #2563eb;
    transform: translateY(-2px);
    box-shadow: 0 6px 10px rgba(59, 130, 246, 0.3);
  }

  .btn-primary:active {
    transform: translateY(0);
    box-shadow: 0 2px 4px rgba(59, 130, 246, 0.2);
  }

  .btn-primary:disabled {
    background: #93c5fd;
    cursor: not-allowed;
    transform: none;
    box-shadow: none;
  }
  
  .separator {
    position: relative;
    margin: 24px 0;
    text-align: center;
  }
  
  .separator::before {
    content: '';
    position: absolute;
    top: 50%;
    left: 0;
    right: 0;
    height: 1px;
    background-color: #e5e7eb;
  }
  
  .separator span {
    position: relative;
    padding: 0 12px;
    background-color: white;
    color: #6b7280;
    font-size: 0.9rem;
    font-weight: 500;
  }
  
  .alt-login-buttons {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 16px;
    margin-bottom: 24px;
  }
  
  .alt-login-btn {
    padding: 12px;
    border: 2px solid #e5e7eb;
    border-radius: 8px;
    background-color: white;
    color: #4b5563;
    font-size: 0.9rem;
    font-weight: 600;
    transition: all 0.2s ease;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
  }
  
  .alt-login-btn:hover {
    background-color: #f9fafb;
    border-color: #3b82f6;
    color: #3b82f6;
    transform: translateY(-1px);
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  }

  .workshop-btn:hover {
    border-color: #3b82f6;
    color: #3b82f6;
  }

  .guest-btn:hover {
    border-color: #059669;
    color: #059669;
  }
  
  .signup-link {
    text-align: center;
    font-size: 0.9rem;
    color: #4b5563;
    margin-top: 24px;
  }
  
  .signup-link a {
    font-weight: 500;
    color: #3b82f6;
    text-decoration: none;
    transition: color 0.2s ease;
  }
  
  .signup-link a:hover {
    color: #2563eb;
    text-decoration: underline;
  }
  
  .alert-error {
    background-color: #fee2e2;
    border: 1px solid #fecaca;
    color: #b91c1c;
    padding: 12px 16px;
    border-radius: 8px;
    margin-bottom: 24px;
    font-size: 0.9rem;
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .loading-spinner {
    display: inline-block;
    width: 1rem;
    height: 1rem;
    border: 2px solid rgba(255, 255, 255, 0.3);
    border-radius: 50%;
    border-top-color: white;
    animation: spin 1s ease-in-out infinite;
    margin-right: 8px;
  }

  @keyframes spin {
    to { transform: rotate(360deg); }
  }
  
  .w-full {
    width: 100%;
  }
</style>
