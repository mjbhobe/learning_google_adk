FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Ensure start script is executable
RUN chmod +x start.sh

# Start the application correctly using a unified start script
CMD ["./start.sh"]
