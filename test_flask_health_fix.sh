#!/bin/bash

echo "🔧 Testing Flask Health Check Fix..."

# Test if the Python health check command works
echo "Testing health check command..."
python3 -c "import requests; requests.get('http://localhost:5000/health').raise_for_status()" 2>/dev/null

if [ $? -eq 0 ]; then
    echo "✅ Health check command works!"
else
    echo "❌ Health check command failed. Make sure Flask service is running."
fi

echo ""
echo "📋 Instructions:"
echo "1. The health check in docker-compose.yml has been updated to use Python instead of curl"
echo "2. Now run: sudo docker-compose down && sudo docker-compose up -d"
echo "3. Check status with: sudo docker-compose ps"
echo "4. Streamlit should now start at http://localhost:8501"