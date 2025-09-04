#!/bin/bash
# Enhanced script to run the Agrigrow application with automatic port selection

echo "Starting Agrigrow application..."

# Find an available port starting from 8080
PORT=8080
while [ $(lsof -i:$PORT -t | wc -l) -ne 0 ]; do
    echo "Port $PORT is in use, trying next port..."
    PORT=$((PORT+1))
    if [ $PORT -gt 8100 ]; then
        echo "Error: Could not find an available port in range 8080-8100"
        exit 1
    fi
done

echo "Found available port: $PORT"
echo "Access the application at: http://127.0.0.1:$PORT"

# Run the application with the available port
FLASK_APP=app.py FLASK_ENV=development python3 -c "import app; app.app.run(debug=True, port=$PORT)"
