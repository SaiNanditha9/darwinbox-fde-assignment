# Approach & Design Decisions

## Approach

I built a full-stack AI-powered employee data analysis application that allows users to upload multiple datasets and ask questions about the data using natural language.

The application accepts employee, attendance, and salary datasets and combines related records using `employee_id`.

The overall flow is:

User Question
→ React Frontend
→ FastAPI Backend
→ Local AI Intent Understanding
→ Deterministic Pandas Analysis
→ Structured Result
→ Frontend Visualization

## Key Design Decisions

### 1. AI for intent understanding, not numerical computation

I used the open-source Qwen2.5 model through Ollama to understand the user's natural-language question and convert it into a structured intent.

The AI does not directly calculate salary or attendance values.

Once the intent is identified, deterministic Pandas functions perform the actual filtering, aggregation, grouping, and calculations.

This approach reduces the risk of incorrect numerical responses from the language model.

### 2. Cross-file analysis

The application supports multiple related datasets.

Employee, attendance, and salary information are joined using `employee_id`, allowing questions that require information from multiple files.

### 3. Local open-source AI

Ollama is used to run the Qwen2.5 model locally.

This avoids requiring a paid external LLM API and keeps the prototype self-contained.

### 4. Structured backend responses

The backend returns structured results containing answers, tabular data, employee information, and chart metadata where appropriate.

This allows the frontend to render results dynamically rather than relying only on plain text.

### 5. Reload persistence

Uploaded datasets are saved locally so they can be restored when the FastAPI development server reloads.

## What I Would Build Next

If I continued developing the application, I would add:

- More flexible natural-language query support
- Additional file types and schema detection
- Better validation for inconsistent datasets
- Authentication and role-based access
- Persistent database storage
- Production deployment
- Streaming AI responses
- More advanced visualizations
- Query history and saved analyses
- Improved observability and error monitoring

## Technology Stack

- React
- JavaScript
- Python
- FastAPI
- Pandas
- Ollama
- Qwen2.5
- CSV / Excel