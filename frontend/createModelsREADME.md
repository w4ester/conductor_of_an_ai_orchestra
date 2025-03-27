# Creating Models in Ollama Workshop Platform

This guide explains how to create, modify, and use custom models in the Ollama Workshop Platform.

## Overview

Models in the Ollama Workshop Platform are built using Ollama's Modelfile format. When you create a model, it is stored directly with Ollama (at `localhost:11434`), making it immediately available for use with both the platform and Ollama CLI.

## Model Components

A model consists of:

1. **Base Model** - The foundation model (like Gemma, Llama, etc.)
2. **Modelfile** - A configuration file with parameters and system prompts
3. **Parameters** - Settings that control model behavior (temperature, tokens, etc.)

## Creating a New Model

### Path
Frontend: `/models/create`  
API Endpoint: `http://localhost:11434/api/create`

### Steps

1. Navigate to the Models section in the sidebar
2. Click "Create New Model"
3. Enter a unique model name (e.g., `workshop-assistant`)
4. Select a base model from the dropdown (e.g., `gemma3:7b`)
5. Edit the Modelfile with your configuration:
   ```
   FROM gemma3:7b
   
   PARAMETER temperature 0.7
   PARAMETER top_p 0.9
   
   SYSTEM You are an AI assistant specialized in helping with programming workshops.
   ```
6. Click "Create Model"

### Modelfile Format

The Modelfile supports several directives:

- `FROM` - Specifies the base model (required)
- `PARAMETER` - Sets runtime parameters
- `SYSTEM` - Defines the system prompt for the model
- `TEMPLATE` - Customizes the prompt format
- `LICENSE` - Documents the license information

## Editing Existing Models

### Path
Frontend: `/models/edit/{model_name}`  
API Endpoint: `http://localhost:11434/api/show` and `http://localhost:11434/api/create`

### Steps

1. Go to the Models section
2. Find your model in the list
3. Click "Edit"
4. Modify the Modelfile
5. Click "Update Model"

## Using Custom Models

Your custom models will be available:

1. In the platform's chat interface
2. When creating new prompts
3. Through the Ollama CLI (`ollama run workshop-assistant`)

## Model Storage

Models are stored by Ollama in:
- macOS: `~/.ollama/models/`
- Linux: `~/.ollama/models/`
- Windows: `%USERPROFILE%\.ollama\models\`

## API Integration

The platform connects directly to Ollama's API:

- `GET http://localhost:11434/api/tags` - List available models
- `POST http://localhost:11434/api/create` - Create/update models
- `DELETE http://localhost:11434/api/delete` - Delete models
- `POST http://localhost:11434/api/show` - Get model information

## Troubleshooting

**Model Creation Fails**
- Ensure Ollama is running (`ollama serve`)
- Check that the base model exists (`ollama list`)
- Verify your Modelfile syntax is correct

**Base Model Not Found**
- Pull the base model first: `ollama pull gemma3:7b`
- Check network connectivity if pulling fails

**Model Not Showing in List**
- Refresh the browser
- Restart the Ollama service
- Check the Ollama logs for errors

## Advanced Usage

### Templates

Use custom templates for specific use cases:

```
TEMPLATE """{{.System}}

User: {{.Prompt}}
Assistant: """
```

### Multimodal Models

For models that support images:

```
FROM llava

PARAMETER temperature 0.7
SYSTEM You are a helpful visual assistant.
```

### Fine-tuned Models

Use locally fine-tuned models:

```
FROM ./my-finetuned-model
```