#!/bin/bash
#used to be only in /api
# Start Ollama in the background
echo "Starting Ollama..."
/bin/ollama serve &

# Wait for Ollama to initialize
echo "Waiting for Ollama to start..."
sleep 10  # Increased sleep time to ensure Ollama is ready

# Check if Ollama is running
if ! pgrep -x "ollama" > /dev/null; then
  echo "Failed to start Ollama. Aborting."
  exit 1
fi

# Pull the required Ollama models
echo "Pulling mxbai-embed-large..."
ollama pull mxbai-embed-large

# echo "Pulling deepseek-r1..."
# ollama pull deepseek-r1

echo "Pulling deepseek-r1:1.5b..."
ollama pull deepseek-r1:1.5b

echo "All required models pulled successfully!"

# Keep the container running
tail -f /dev/null