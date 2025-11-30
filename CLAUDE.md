# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a FastAPI-based backend project for stock-related services. The project uses Python 3.12 and is in its initial development phase.

## Development Setup

**Virtual Environment**: The project uses a virtual environment located in `.venv/`

Activate the virtual environment:
```bash
# Windows
.venv\Scripts\activate

# Linux/Mac
source .venv/bin/activate
```

Install dependencies:
```bash
pip install fastapi uvicorn pydantic
```

## Running the Application

Start the development server:
```bash
uvicorn main:app --reload
```

The server will be available at `http://127.0.0.1:8000`

API documentation is auto-generated at:
- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

## Project Structure

Currently minimal with a single entry point:
- `main.py` - FastAPI application with basic endpoints
- `test_main.http` - HTTP test file for manual API testing

## Architecture Notes

- **Framework**: FastAPI for async API development
- **ASGI Server**: Uvicorn for running the application
- **Validation**: Pydantic for data validation and serialization
- The project follows async/await patterns for route handlers
