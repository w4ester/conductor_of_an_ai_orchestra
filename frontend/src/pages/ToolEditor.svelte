<script lang="ts">
  import { onMount } from 'svelte';
  import { api } from '../lib/api';
  import { toolsStore } from '../lib/store';
  import type { Tool } from '../lib/api';
  
  // Props
  export let toolId = '';
  export let isEdit = false; // true for edit, false for create
  
  // State
  let name = '';
  let description = '';
  let code = '';
  let language = 'python';
  let isSaving = false;
  let isRunning = false;
  let testParams = '';
  let error = '';
  let success = '';
  let testResult = '';
  
  // Template examples
  const templates = {
    weather: `# Weather Information Tool
# This tool gets current weather information for a location

def get_weather(location):
    """
    Get current weather for a location
    
    Args:
        location (str): The city or location to get weather for
        
    Returns:
        dict: Weather information including temperature, conditions, etc.
    """
    # In a real implementation, you would call a weather API
    # For demonstration, we'll return mock data
    return {
        "location": location,
        "temperature": 72,
        "conditions": "Partly Cloudy",
        "humidity": 65,
        "wind": "5 mph"
    }
`,
    search: `# Web Search Tool
# This tool performs a web search and returns results

def search_web(query, num_results=5):
    """
    Search the web for information
    
    Args:
        query (str): The search query
        num_results (int): Number of results to return
        
    Returns:
        list: Search results
    """
    # In a real implementation, you would call a search API
    # For demonstration, we'll return mock data
    return [
        {"title": f"Result 1 for {query}", "url": "https://example.com/1", "snippet": "This is the first result"},
        {"title": f"Result 2 for {query}", "url": "https://example.com/2", "snippet": "This is the second result"},
        {"title": f"Result 3 for {query}", "url": "https://example.com/3", "snippet": "This is the third result"}
    ][:num_results]
`,
    calculator: `# Calculator Tool
# This tool performs mathematical calculations

def calculate(expression):
    """
    Evaluate a mathematical expression
    
    Args:
        expression (str): The math expression to evaluate
        
    Returns:
        float: The result of the calculation
    """
    # This is a simple calculator that evaluates expressions
    # CAUTION: In a real implementation, you would want to add safety checks
    try:
        # Only allow basic operations and numbers for security
        allowed_chars = set("0123456789+-*/().^ ")
        for char in expression:
            if char not in allowed_chars:
                raise ValueError(f"Invalid character in expression: {char}")
                
        # Replace ^ with ** for exponentiation
        expression = expression.replace('^', '**')
        
        # Evaluate the expression
        result = eval(expression)
        return result
    except Exception as e:
        return {"error": str(e)}
`
  };
  
  // Load tool data if in edit mode
  onMount(async () => {
    if (isEdit && toolId) {
      try {
        // Load tool data
        const tool = await api.getTool(toolId);
        
        name = tool.name;
        description = tool.description;
        code = tool.code;
        language = tool.language || 'python';
      } catch (err) {
        console.error('Failed to load tool:', err);
        error = 'Failed to load tool. Please try again.';
      }
    } else {
      // Default for new tool
      name = '';
      description = '';
      code = templates.weather;
      language = 'python';
    }
  });
  
  // Apply template
  function applyTemplate(template) {
    code = templates[template];
  }
  
  // Test tool
  async function testTool() {
    if (!code) {
      error = 'Please enter code for your tool';
      return;
    }
    
    if (!toolId && !isEdit) {
      // For new tools that haven't been saved yet, just show a message
      success = 'Tool must be saved before testing. Click "Save Tool" and then test.';
      return;
    }
    
    try {
      isRunning = true;
      error = '';
      success = '';
      testResult = '';
      
      // Parse parameters
      let params = {};
      if (testParams.trim()) {
        try {
          params = JSON.parse(testParams);
        } catch (err) {
          error = 'Invalid JSON parameters. Please check your format.';
          isRunning = false;
          return;
        }
      }
      
      // Call the test endpoint
      const result = await api.testTool(toolId, params);
      
      testResult = JSON.stringify(result, null, 2);
      success = 'Tool executed successfully!';
    } catch (err) {
      console.error('Failed to test tool:', err);
      error = `Failed to test tool: ${err.message}`;
    } finally {
      isRunning = false;
    }
  }
  
  // Save tool
  async function saveTool() {
    if (!name.trim()) {
      error = 'Please enter a name';
      return;
    }
    
    if (!description.trim()) {
      error = 'Please enter a description';
      return;
    }
    
    if (!code.trim()) {
      error = 'Please enter code for your tool';
      return;
    }
    
    try {
      isSaving = true;
      error = '';
      success = '';
      
      // Create tool object
      const toolData: Tool = {
        name,
        description,
        code,
        language
      };
      
      let savedTool;
      
      if (isEdit && toolId) {
        // Update existing tool
        savedTool = await api.updateTool(toolId, toolData);
      } else {
        // Create new tool
        savedTool = await api.createTool(toolData);
        // Update toolId so we can test it
        toolId = savedTool.id;
      }
      
      // Refresh tools list
      const tools = await api.getTools();
      toolsStore.set(tools);
      
      success = `Tool "${name}" has been ${isEdit ? 'updated' : 'created'} successfully`;
      
      // If creating a new tool, switch to edit mode
      if (!isEdit) {
        isEdit = true;
        // Update URL without reloading
        window.history.replaceState({}, '', `#/tools/edit/${toolId}`);
      }
    } catch (err) {
      console.error('Failed to save tool:', err);
      error = `Failed to ${isEdit ? 'update' : 'create'} tool: ${err.message}`;
    } finally {
      isSaving = false;
    }
  }
  
  // Delete tool
  async function deleteTool() {
    if (!confirm(`Are you sure you want to delete the tool "${name}"? This cannot be undone.`)) {
      return;
    }
    
    try {
      isSaving = true;
      error = '';
      success = '';
      
      await api.deleteTool(toolId);
      
      // Refresh tools list
      const tools = await api.getTools();
      toolsStore.set(tools);
      
      success = `Tool "${name}" has been deleted successfully`;
      
      // Go back to tools list after a short delay
      setTimeout(() => {
        window.location.hash = '/tools';
      }, 1500);
    } catch (err) {
      console.error('Failed to delete tool:', err);
      error = `Failed to delete tool: ${err.message}`;
    } finally {
      isSaving = false;
    }
  }
  
  // Cancel editing
  function cancel() {
    window.history.back();
  }
</script>

<div style="padding: 1.5rem;">
  <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem;">
    <h1 style="font-size: 1.5rem; font-weight: bold;">{isEdit ? 'Edit' : 'Create'} Tool</h1>
    <div style="display: flex; gap: 0.5rem;">
      <button 
        on:click={cancel}
        style="padding: 0.5rem 1rem; border: 1px solid #d1d5db; border-radius: 0.25rem; background-color: white;"
      >
        Cancel
      </button>
      {#if isEdit}
        <button 
          on:click={deleteTool}
          disabled={isSaving}
          style="padding: 0.5rem 1rem; border-radius: 0.25rem; background-color: #ef4444; color: white; opacity: ${isSaving ? '0.7' : '1'};"
        >
          Delete Tool
        </button>
      {/if}
      <button 
        on:click={saveTool}
        disabled={isSaving}
        style="padding: 0.5rem 1rem; border-radius: 0.25rem; background-color: #2563eb; color: white; opacity: ${isSaving ? '0.7' : '1'};"
      >
        {isSaving ? 'Saving...' : isEdit ? 'Update Tool' : 'Save Tool'}
      </button>
    </div>
  </div>
  
  {#if error}
    <div style="background-color: #fee2e2; border: 1px solid #f87171; color: #b91c1c; padding: 0.75rem 1rem; border-radius: 0.25rem; margin-bottom: 1rem;" role="alert">
      <span>{error}</span>
    </div>
  {/if}
  
  {#if success}
    <div style="background-color: #d1fae5; border: 1px solid #34d399; color: #065f46; padding: 0.75rem 1rem; border-radius: 0.25rem; margin-bottom: 1rem;" role="alert">
      <span>{success}</span>
    </div>
  {/if}
  
  <div style="display: grid; grid-template-columns: 1fr 300px; gap: 1.5rem;">
    <!-- Main editor area -->
    <div>
      <!-- Tool details section -->
      <div style="background-color: white; padding: 1.5rem; border-radius: 0.5rem; box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06); margin-bottom: 1.5rem;">
        <div style="margin-bottom: 1rem;">
          <label for="name" style="display: block; font-size: 0.875rem; font-weight: 500; margin-bottom: 0.25rem;">
            Tool Name
          </label>
          <input 
            type="text" 
            id="name" 
            bind:value={name}
            style="width: 100%; padding: 0.5rem 0.75rem; border: 1px solid #d1d5db; border-radius: 0.375rem; box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);"
            placeholder="e.g., Weather Information Tool"
          />
        </div>
        
        <div>
          <label for="description" style="display: block; font-size: 0.875rem; font-weight: 500; margin-bottom: 0.25rem;">
            Description
          </label>
          <textarea 
            id="description" 
            bind:value={description}
            style="width: 100%; height: 80px; padding: 0.5rem 0.75rem; border: 1px solid #d1d5db; border-radius: 0.375rem; box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05); resize: vertical;"
            placeholder="Describe what your tool does and how to use it..."
          ></textarea>
        </div>
      </div>
      
      <!-- Code editor section -->
      <div style="background-color: white; padding: 1.5rem; border-radius: 0.5rem; box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06); margin-bottom: 1.5rem;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem;">
          <label for="code" style="display: block; font-size: 0.875rem; font-weight: 500;">
            Tool Code
          </label>
          <div style="display: flex; gap: 0.5rem; align-items: center;">
            <span style="font-size: 0.875rem;">Language:</span>
            <select
              bind:value={language}
              style="padding: 0.25rem 0.5rem; border: 1px solid #d1d5db; border-radius: 0.25rem; font-size: 0.875rem;"
            >
              <option value="python">Python</option>
              <option value="javascript">JavaScript</option>
            </select>
          </div>
        </div>
        
        <textarea 
          id="code" 
          bind:value={code}
          style="width: 100%; height: 300px; padding: 0.5rem 0.75rem; border: 1px solid #d1d5db; border-radius: 0.375rem; box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05); resize: vertical; font-family: monospace; line-height: 1.5;"
          placeholder="# Write your tool code here..."
        ></textarea>
      </div>
      
      <!-- Test section -->
      <div style="background-color: white; padding: 1.5rem; border-radius: 0.5rem; box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);">
        <h2 style="font-size: 1.125rem; font-weight: 500; margin-bottom: 1rem;">Test Your Tool</h2>
        
        <div style="margin-bottom: 1rem;">
          <label for="params" style="display: block; font-size: 0.875rem; font-weight: 500; margin-bottom: 0.25rem;">
            Parameters (JSON)
          </label>
          <textarea 
            id="params" 
            bind:value={testParams}
            style="width: 100%; height: 100px; padding: 0.5rem 0.75rem; border: 1px solid #d1d5db; border-radius: 0.375rem; box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05); resize: vertical; font-family: monospace;"
            placeholder={`{"location": "New York"}`}
          ></textarea>
        </div>
        
        <div style="display: flex; justify-content: flex-end;">
          <button 
            on:click={testTool}
            disabled={isRunning}
            style="padding: 0.5rem 1rem; border-radius: 0.25rem; background-color: #8b5cf6; color: white; opacity: ${isRunning ? '0.7' : '1'};"
          >
            {isRunning ? 'Running...' : 'Test Tool'}
          </button>
        </div>
        
        {#if testResult}
          <div style="margin-top: 1rem;">
            <label style="display: block; font-size: 0.875rem; font-weight: 500; margin-bottom: 0.25rem;">
              Test Result
            </label>
            <div style="padding: 1rem; background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 0.375rem; font-family: monospace; white-space: pre-wrap;">
              {testResult}
            </div>
          </div>
        {/if}
      </div>
    </div>
    
    <!-- Sidebar -->
    <div>
      <!-- Templates section -->
      <div style="background-color: white; padding: 1.5rem; border-radius: 0.5rem; box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06); margin-bottom: 1.5rem;">
        <h2 style="font-size: 1.125rem; font-weight: 500; margin-bottom: 1rem;">Tool Templates</h2>
        
        <div style="display: flex; flex-direction: column; gap: 0.5rem;">
          <button 
            on:click={() => applyTemplate('weather')}
            style="text-align: left; padding: 0.5rem; border: 1px solid #d1d5db; border-radius: 0.25rem; background-color: #f9fafb;"
          >
            Weather Information Tool
          </button>
          <button 
            on:click={() => applyTemplate('search')}
            style="text-align: left; padding: 0.5rem; border: 1px solid #d1d5db; border-radius: 0.25rem; background-color: #f9fafb;"
          >
            Web Search Tool
          </button>
          <button 
            on:click={() => applyTemplate('calculator')}
            style="text-align: left; padding: 0.5rem; border: 1px solid #d1d5db; border-radius: 0.25rem; background-color: #f9fafb;"
          >
            Calculator Tool
          </button>
        </div>
      </div>
      
      <!-- Help section -->
      <div style="background-color: white; padding: 1.5rem; border-radius: 0.5rem; box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);">
        <h2 style="font-size: 1.125rem; font-weight: 500; margin-bottom: 1rem;">Tool Development Guide</h2>
        
        <div style="font-size: 0.875rem;">
          <h3 style="font-weight: 500; margin-bottom: 0.5rem;">Best Practices</h3>
          <ul style="list-style: disc; margin-left: 1.5rem; margin-bottom: 1rem;">
            <li>Always document your functions with docstrings</li>
            <li>Include proper error handling</li>
            <li>Validate and sanitize inputs</li>
            <li>Keep tools focused on a single task</li>
            <li>Return well-structured data (dictionaries or lists)</li>
          </ul>
          
          <h3 style="font-weight: 500; margin-bottom: 0.5rem;">Using with Ollama</h3>
          <p style="margin-bottom: 0.5rem;">Tools can be integrated with Ollama using function calling capabilities.</p>
          <p>For more information, refer to the <a href="https://github.com/ollama/ollama/blob/main/docs/tutorials/function-calling.md" target="_blank" style="color: #2563eb;">Ollama function calling documentation</a>.</p>
        </div>
      </div>
    </div>
  </div>
</div>