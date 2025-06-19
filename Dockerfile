# Use official Playwright image with all browser dependencies
FROM mcr.microsoft.com/playwright/python:v1.52.0-jammy

# Set working directory inside the container
WORKDIR /app

# Copy everything from your repo to the image
COPY . /app

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Expose your API
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]
