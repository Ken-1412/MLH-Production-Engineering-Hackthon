FROM python:3.13-slim

RUN pip install uv

WORKDIR /app

# Copy dependency files first for layer caching
COPY pyproject.toml uv.lock* ./
RUN uv sync --frozen

# Copy application code
COPY . .

# Non-root user for security
RUN useradd -m -u 1001 appuser && chown -R appuser /app
USER appuser

EXPOSE 5000

# Use the module-level `app` from run.py — matches template structure
CMD ["uv", "run", "gunicorn", \
     "--workers", "2", \
     "--bind", "0.0.0.0:5000", \
     "--timeout", "30", \
     "--access-logfile", "-", \
     "--error-logfile", "-", \
     "run:app"]
