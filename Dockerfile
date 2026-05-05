# Stage 1: Build the Next.js frontend
FROM node:18-alpine AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm install
COPY frontend ./
RUN npm run build

# Stage 2: Build the Python backend and serve
FROM python:3.10-slim AS backend
WORKDIR /app

# Install system dependencies if any
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY pyproject.toml ./
# We can install dependencies from pyproject.toml using pip
RUN pip install --no-cache-dir .

# Copy the backend code
COPY macro_dashboard/ ./macro_dashboard/

# Copy the data directory
COPY data_demo/ ./data_demo/

# Copy the built frontend from Stage 1
COPY --from=frontend-builder /app/frontend/out ./frontend/out

# Expose the standard Cloud Run port
EXPOSE 8080

# Command to run the application using uvicorn
CMD ["uvicorn", "macro_dashboard.main:app", "--host", "0.0.0.0", "--port", "8080"]
