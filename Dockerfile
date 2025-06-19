FROM python:3.10

WORKDIR /app

# Install system dependencies for headless browser
RUN apt-get update && \
    apt-get install -y wget gnupg libnss3 libatk1.0-0 libatk-bridge2.0-0 \
    libcups2 libxkbcommon0 libxcomposite1 libxdamage1 libxrandr2 libgbm1 \
    libasound2 libxshmfence1 libpangocairo-1.0-0 libgtk-3-0 libdrm2 && \
    apt-get clean

# Install Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ✅ This installs the browser binaries
RUN playwright install --with-deps

# Copy app code
COPY . .

# Expose app port for Render
EXPOSE 10000

# Run the API
CMD ["uvicorn", "main:app", "--host=0.0.0.0", "--port=10000"]
