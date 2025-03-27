# Creating and Managing Prompts in Ollama Workshop Platform

This guide explains how to create, organize, and use prompts in the Ollama Workshop Platform.

## Overview

Prompts are pre-defined templates that help guide AI model responses. The platform stores these prompts in a database, allowing you to build a library of reusable templates for different scenarios.

## Prompt Components

A prompt consists of:

1. **Title** - A descriptive name
2. **Content** - The actual prompt text
3. **Model** - The associated model this prompt works best with
4. **Category** - Optional grouping for organization
5. **Tags** - Optional labels for filtering and search

## Creating a New Prompt

### Path
Frontend: `/prompts/create`  
API Endpoint: `http://localhost:8000/api/prompts`

### Steps

1. Navigate to the Prompts section in the sidebar
2. Click "Create New Prompt"
3. Fill in the form:
   - **Title**: Enter a descriptive name (e.g., "Code Review Assistant")
   - **Model**: Select the model to use with this prompt
   - **Category**: Choose or create a category (e.g., "Development")
   - **Tags**: Add relevant tags (e.g., "code", "review")
   - **Content**: Write your prompt template:
     ```
     Review the following code snippet and suggest improvements:
     
     ```{{language}}
     {{code}}
     ```
     
     Focus on:
     - Code quality and readability
     - Potential bugs or edge cases
     - Performance improvements
     - Best practices
     ```
4. Click "Save Prompt"

## Using Variables in Prompts

Prompts can include variable placeholders that get replaced when used:

- Use double curly braces: `{{variable_name}}`
- Common examples: `{{code}}`, `{{language}}`, `{{question}}`
- When using the prompt, you'll be asked to provide values for these variables

## Managing Prompts

### Path
Frontend: `/prompts`  
API Endpoint: `http://localhost:8000/api/prompts`

### Available Actions

- **View All Prompts**: Browse your prompt library
- **Search/Filter**: Find prompts by title, category, or tags
- **Edit**: Modify existing prompts
- **Delete**: Remove prompts you no longer need
- **Clone**: Create a new prompt based on an existing one

## Using Prompts in Chat

### Path
Frontend: `/chat`  
API Endpoint: `http://localhost:8000/api/chat`

### Steps

1. Open the chat interface
2. Click "Load Prompt" in the message input area
3. Select a prompt from your library
4. Fill in any variables the prompt requires
5. Send the message

## Database Storage

Prompts are stored in the platform's database:

- In development/local: In-memory storage (prompts_db)
- In production: PostgreSQL or other persistent database
- Schema: id, title, content, model, category, tags, created_by, created_at, updated_at

## API Integration

The platform provides REST API endpoints for prompt management:

- `GET /api/prompts` - List all prompts
- `GET /api/prompts/{id}` - Get a specific prompt
- `POST /api/prompts` - Create a new prompt
- `PUT /api/prompts/{id}` - Update a prompt
- `DELETE /api/prompts/{id}` - Delete a prompt

## Prompt Categories

Organize prompts by categories such as:

- **Writing**: Content creation, summaries, outlines
- **Development**: Code generation, debugging, documentation
- **Education**: Explanations, learning materials
- **Business**: Emails, reports, analysis
- **Creative**: Storytelling, brainstorming

## Best Practices

1. **Be Specific**: Clearly define what you want the model to do
2. **Use Examples**: Include examples of desired outputs when possible
3. **Structure Output**: Specify format when needed (JSON, Markdown, etc.)
4. **Test and Iterate**: Refine prompts based on actual model responses
5. **Share Effective Prompts**: Build a library of proven templates

## Example Prompts

### Code Explainer
```
Explain this {{language}} code in simple terms:

```{{language}}
{{code}}
```

Break down:
1. What the code does
2. How it works
3. Key functions or methods
4. Any potential issues
```

### Brainstorming Assistant
```
I need ideas for {{topic}}. 

Generate 5 creative ideas that:
- Are innovative
- Address the problem of {{problem}}
- Consider the target audience of {{audience}}

For each idea, provide:
- A catchy title
- A brief description
- One key benefit
- One potential challenge
```