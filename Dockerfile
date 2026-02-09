# Use Python 3.12 slim image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install uv for dependency management
RUN pip install uv

# Copy dependency files and source code (needed for build)
COPY pyproject.toml uv.lock README.md ./
COPY bharatgen_openai/ ./bharatgen_openai/

# Install dependencies
RUN uv sync --frozen

# Expose the default port
EXPOSE 8000

# Set environment variables with defaults
ENV BHARATGEN_HOST=0.0.0.0
ENV BHARATGEN_PORT=8000
ENV BHARATGEN_API_KEYS=sk-test-key

# Run the server
CMD ["uv", "run", "python", "-m", "bharatgen_openai.server"]
