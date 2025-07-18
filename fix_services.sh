#!/bin/bash

# fix_services.sh - Quick Fix Script for Service Issues
# Addresses Zookeeper, Kafka, and Spark dependency issues

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
COMPOSE_FILE="docker-compose-robust.yml"

# Logging functions
log_info() {
    echo -e "${CYAN}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_step() {
    echo -e "${PURPLE}[STEP]${NC} $1"
}

# Function to check if Docker Compose is available
check_docker() {
    if command -v docker-compose &> /dev/null; then
        DOCKER_CMD="docker-compose"
    elif command -v docker &> /dev/null; then
        DOCKER_CMD="docker compose"
    else
        log_error "Docker/Docker Compose not found. Please install Docker."
        return 1
    fi
    
    log_success "Using Docker command: $DOCKER_CMD"
    return 0
}

# Function to restart services in proper order
restart_services_ordered() {
    log_step "Stopping problematic services..."
    
    # Stop services in reverse dependency order
    $DOCKER_CMD -f $COMPOSE_FILE stop streamlit-app spark-worker spark-master kafka zookeeper 2>/dev/null || true
    
    log_step "Starting services in dependency order..."
    
    # Start Zookeeper first
    log_info "Starting Zookeeper..."
    $DOCKER_CMD -f $COMPOSE_FILE up -d zookeeper
    
    # Wait for Zookeeper to be healthy
    log_info "Waiting for Zookeeper to be healthy..."
    for i in {1..30}; do
        if $DOCKER_CMD -f $COMPOSE_FILE exec -T zookeeper bash -c "echo 'ruok' | nc -w 2 localhost 2181" 2>/dev/null | grep -q "imok"; then
            log_success "Zookeeper is healthy"
            break
        fi
        echo -n "."
        sleep 2
    done
    
    # Start Kafka
    log_info "Starting Kafka..."
    $DOCKER_CMD -f $COMPOSE_FILE up -d kafka
    
    # Wait for Kafka to be healthy
    log_info "Waiting for Kafka to be healthy..."
    for i in {1..30}; do
        if $DOCKER_CMD -f $COMPOSE_FILE exec -T kafka kafka-topics.sh --bootstrap-server localhost:9092 --list > /dev/null 2>&1; then
            log_success "Kafka is healthy"
            break
        fi
        echo -n "."
        sleep 3
    done
    
    # Start Spark services
    log_info "Starting Spark services..."
    $DOCKER_CMD -f $COMPOSE_FILE up -d spark-master spark-worker
    
    # Start remaining services
    log_info "Starting remaining services..."
    $DOCKER_CMD -f $COMPOSE_FILE up -d
    
    log_success "All services started. Health checks will continue in the background."
}

# Function to fix common issues
fix_common_issues() {
    log_step "Applying common fixes..."
    
    # Clean up any orphaned containers
    log_info "Cleaning up orphaned containers..."
    $DOCKER_CMD -f $COMPOSE_FILE down --remove-orphans 2>/dev/null || true
    
    # Prune unused networks
    log_info "Cleaning unused networks..."
    docker network prune -f 2>/dev/null || true
    
    # Remove any stuck volumes (if safe to do so)
    log_info "Checking for stuck volumes..."
    # Note: We don't automatically remove volumes to preserve data
    
    log_success "Common fixes applied"
}

# Function to verify fixes
verify_fixes() {
    log_step "Verifying service health..."
    
    sleep 10  # Give services time to start
    
    # Check each critical service
    local services=("redis" "neo4j" "zookeeper" "kafka")
    local all_healthy=true
    
    for service in "${services[@]}"; do
        if $DOCKER_CMD -f $COMPOSE_FILE ps $service | grep -q "healthy\|Up"; then
            log_success "$service is running"
        else
            log_warning "$service may still have issues"
            all_healthy=false
        fi
    done
    
    if $all_healthy; then
        log_success "All critical services appear to be running"
        log_info "Dashboard should be available at http://localhost:8501"
        log_info "Spark UI should be available at http://localhost:8080"
        log_info "Neo4j browser should be available at http://localhost:7474"
    else
        log_warning "Some services may still need attention"
        log_info "Run './check_service_health.sh' for detailed diagnostics"
    fi
}

# Main execution
main() {
    echo ""
    log_info "=== FIXING SERVICE ISSUES ==="
    echo ""
    
    # Check Docker
    if ! check_docker; then
        exit 1
    fi
    
    # Apply fixes
    fix_common_issues
    
    # Restart services in proper order
    restart_services_ordered
    
    # Verify the fixes
    verify_fixes
    
    echo ""
    log_info "=== FIX COMPLETE ==="
    echo ""
    log_info "Next steps:"
    echo "  1. Run './check_service_health.sh' to verify all services"
    echo "  2. Check the dashboard at http://localhost:8501"
    echo "  3. If issues persist, check individual service logs:"
    echo "     $DOCKER_CMD -f $COMPOSE_FILE logs [service-name]"
    echo ""
}

# Run the main function
main "$@"