# Flask Service Issue - Complete Solution

## Problem
The Flask LLM service is still showing merge conflict errors even after rebuilding:
```
IndentationError: expected an indented block
flask-llm-service  |     <<<<<<< Updated upstream
```

## Root Cause
Docker is using cached layers from a previous build that contained merge conflicts. The `--build` flag doesn't always clear all cached layers.

## Solution
You need to force a complete rebuild without using any Docker cache. Here are the steps:

### Method 1: Use the Force Rebuild Script (Recommended)
I've created a script that will do everything for you:

```bash
# Make sure you're in the project directory
cd ~/synapse-lite

# Run the force rebuild script
./force_rebuild.sh
```

### Method 2: Manual Steps
If you prefer to do it manually:

```bash
# 1. Stop all containers and remove volumes
docker compose down -v

# 2. Remove all project-related Docker images
docker rmi -f $(docker images | grep synapse-lite | awk '{print $3}')

# 3. Prune Docker system to remove cached layers
docker system prune -af

# 4. Build without cache
docker compose build --no-cache

# 5. Start services
docker compose up -d
```

### Method 3: Alternative - Remove just the Flask service image
If you want to be more targeted:

```bash
# Stop services
docker compose down

# Remove only the Flask service image
docker rmi -f synapse-lite-flask-llm-service

# Rebuild just the Flask service without cache
docker compose build --no-cache flask-llm-service

# Start services
docker compose up -d
```

## Verification
After rebuilding, check if the Flask service is working:

```bash
# Check Flask service logs
docker compose logs flask-llm-service

# You should see something like:
# [INFO] Starting gunicorn 23.0.0
# [INFO] Listening at: http://0.0.0.0:5000 (1)
# [INFO] Booting worker with pid: 7
# WITHOUT the merge conflict error

# Test the health endpoint
curl http://localhost:5000/health
```

## Files Status
- ✅ `ai_service/app.py` - Clean, no merge conflicts, valid Python syntax
- ✅ `docker-compose.yml` - All issues fixed
- ✅ `streamlit_app/Dockerfile` - Fixed COPY commands
- ✅ `force_rebuild.sh` - Script created for complete rebuild

## Why This Happened
Docker's layer caching system sometimes preserves old layers even when using `--build`. This can happen when:
1. The build context hasn't changed significantly
2. Docker thinks it can reuse cached layers
3. Previous builds with merge conflicts got cached

The `--no-cache` flag forces Docker to rebuild every layer from scratch, ensuring the current clean files are used.

## Prevention
To avoid this in the future:
1. Always resolve merge conflicts before building
2. Use `--no-cache` when you suspect caching issues
3. Regularly clean Docker system with `docker system prune`