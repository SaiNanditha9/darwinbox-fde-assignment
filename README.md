# Darwinbox FDE Assignment

## AI-Powered Data Analysis Prototype

A full-stack prototype that allows users to upload employee datasets and ask natural-language questions across multiple files.

The application uses an open-source local LLM to understand the user's question and converts it into a structured analysis intent. The actual calculations are performed deterministically using Pandas.

## Features

- Upload multiple CSV files
- Analyze data across multiple datasets
- Natural-language questions
- Employee salary analysis
- Attendance analysis
- Department-wise salary analysis
- Attendance filtering
- Attendance trends
- Tables and charts in the frontend
- Local open-source AI model using Ollama and Qwen2.5
- Uploaded datasets persist across backend reloads

## Architecture

```text
User
  |
  v
React Frontend
  |
  v
FastAPI Backend
  |
  +----------------------+
  |                      |
  v                      v
Ollama / Qwen2.5     Uploaded Data
  |                      |
  v                      v
Intent Extraction    Pandas Analysis
  |                      |
  +----------+-----------+
             |
             v
        Analysis Result
             |
             v
       React UI / Charts
