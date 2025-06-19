FROM python:3.10

# Set working directory
WORKDIR /app

# Install system dependencies for Playwright
RUN apt-get update && \
    apt-get install -y wget gnupg curl libnss3 libatk1.0-0 libatk-bridge2.0-0 \
    libcups2 libxkbcommon0 libxcomposite1 libxdamage1 libxrandr2 libgbm1 \
    libasound2 libxshmfence1 libpangocairo-1.0-0 libgtk-3-0 libdrm2 \
    fonts-liberation ca-certificates && \
    apt-get clean

# Install Node.js (required for Playwright browsers)
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - && \
    apt-get install -y nodejs

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers with dependencies
RUN playwright install --with-deps

# Copy all app files
COPY . .

# Expose port used by Uvicorn
EXPOSE 10000

# Start the FastAPI server
CMD ["uvicorn", "main:app", "--host=0.0.0.0", "--port=10000"]
