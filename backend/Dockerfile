FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Ensure data directory exists
RUN mkdir -p /app/data

# Expose API port
EXPOSE 8000

# Script to run migrations and start the server
RUN echo '#!/bin/sh\n\
python app/db/init_db.py\n\
if [ "$ROLE" = "worker" ]; then\n\
  echo "Starting worker node..."\n\
  python app/worker.py\n\
else\n\
  echo "Starting API server node..."\n\
  uvicorn app.main:app --host 0.0.0.0 --port 8000\n\
fi' > /app/entrypoint.sh && chmod +x /app/entrypoint.sh

# Run
ENTRYPOINT ["/app/entrypoint.sh"]
