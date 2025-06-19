FROM python:3.10

WORKDIR /app

# Install system dependencies for headless browser support
RUN apt-get update && \
    apt-get install -y wget gnupg curl libnss3 libatk1.0-0 libatk-bridge2.0-0 \
    libcups2 libxkbcommon0 libxcomposite1 libxdamage1 libxrandr2 libgbm1 \
    libasound2 libxshmfence1 libpangocairo-1.0-0 libgtk-3-0 libdrm2 \
    libenchant-2-2 libsecret-1-0 libavif13 libmanette-0.2-0 libgles2 \
    fonts-liberation libgraphene-1.0-0 libgstgl-1.0-0 libgstcodecparsers-1.0-0 \
    ca-certificates gnupg && \
    curl -fsSL https://deb.nodesource.com/setup_18.x | bash - && \
    apt-get install -y nodejs && \
    apt-get clean

# Install Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright and browser binaries
RUN playwright install --with-deps

# Copy app code
COPY . .

EXPOSE 10000

CMD ["uvicorn", "main:app", "--host=0.0.0.0", "--port=10000"]
