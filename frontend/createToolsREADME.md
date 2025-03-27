# Creating and Using Tools in Ollama Workshop Platform

This guide explains how to create, manage, and use custom tools that extend your AI models' capabilities in the Ollama Workshop Platform.

## Overview

Tools are custom functions that models can use to perform actions beyond text generation, such as retrieving information, performing calculations, or interacting with external systems.

## Tool Components

A tool consists of:

1. **Name** - A descriptive identifier
2. **Description** - What the tool does and when to use it
3. **Code** - The actual implementation (typically Python)
4. **Language** - The programming language used (default: Python)
5. **Parameters** - Inputs the tool accepts

## Creating a New Tool

### Path
Frontend: `/tools/create`  
API Endpoint: `http://localhost:8000/api/tools`

### Steps

1. Navigate to the Tools section in the sidebar
2. Click "Create New Tool"
3. Fill in the form:
   - **Name**: Enter a descriptive name (e.g., "WeatherLookup")
   - **Description**: Explain what the tool does and when to use it
   - **Language**: Select the programming language (default: Python)
   - **Code**: Write your tool implementation:
     ```python
     import requests
     
     def get_weather(location):
         """Get current weather for a location.
         
         Args:
             location (str): City name or zip code
             
         Returns:
             dict: Weather information
         """
         # Replace with your actual API key
         api_key = "demo_key"
         url = f"https://api.example.com/weather?location={location}&key={api_key}"
         
         try:
             response = requests.get(url)
             response.raise_for_status()
             data = response.json()
             return {
                 "temperature": data["current"]["temp_c"],
                 "condition": data["current"]["condition"]["text"],
                 "humidity": data["current"]["humidity"],
                 "wind": data["current"]["wind_kph"]
             }
         except Exception as e:
             return {"error": str(e)}
     ```
4. Click "Save Tool"

## Tool Security

All tools execute in a sandboxed environment with:

- Limited execution time (timeout protection)
- Restricted network access (only approved domains)
- No file system access outside designated directories
- Memory usage limits

## Testing Tools

### Path
Frontend: `/tools/{tool_id}/test`  
API Endpoint: `http://localhost:8000/api/tools/{tool_id}/test`

### Steps

1. Open the tool details page
2. Click "Test Tool"
3. Enter test parameters
4. View the execution results

## Using Tools with Models

Models can use tools during conversations when:

1. The tool is explicitly made available to the model
2. The context of the conversation requires the tool's functionality

### Example Chat with Tool Use

User: "What's the weather like in New York?"

System: *Makes a tool call to WeatherLookup with parameter location="New York"*

Tool: Returns `{"temperature": 62, "condition": "Partly cloudy", "humidity": 65, "wind": 8}`