FROM python:3.10-slim

# Install system utilities
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Setup non-root execution permissions for HF Spaces (UID 1000)
RUN useradd -m -u 1000 user
USER user

# Set up environment variables
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH \
    PYTHONPATH=/home/user/app \
    HF_HOME=/home/user/.cache/huggingface \
    HF_HUB_DISABLE_SYMLINKS_WARNING=1

# Set the working directory
WORKDIR $HOME/app

# Copy requirements first to leverage Docker layer caching
COPY --chown=user:user requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Copy source code and config
COPY --chown=user:user . .

# Expose Hugging Face Spaces default port
EXPOSE 7860

# Run uvicorn server binding to port 7860
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]
