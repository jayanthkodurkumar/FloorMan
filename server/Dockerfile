FROM python:3.12-slim

WORKDIR /app

# Install uv
RUN pip install --no-cache-dir uv

# Copy dependency files and install
COPY pyproject.toml uv.lock ./
RUN uv sync --no-dev --frozen

# Copy source code
COPY . .

EXPOSE 8000

CMD ["uv", "run", "python", "-m", "uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
