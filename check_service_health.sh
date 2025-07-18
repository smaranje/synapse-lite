#!/bin/bash

# check_service_health.sh - Service Health Monitoring Script
# Provides detailed health status for all services in the pipeline

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
    echo -e "${GREEN}[✅ HEALTHY]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[⚠️  WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[❌ UNHEALTHY]${NC} $1"
}

log_step() {
    echo -e "${PURPLE}[CHECKING]${NC} $1"
}

# Function to check if Docker Compose is available
check_docker() {
    if ! command -v docker-compose &> /dev/null && ! command -v docker &> /dev/null; then
        log_error "Docker/Docker Compose not found. Please install Docker."
        return 1
    fi
    
    if command -v docker-compose &> /dev/null; then
        DOCKER_CMD="docker-compose"
    else
        DOCKER_CMD="docker compose"
    fi
    
    log_success "Docker Compose found: $DOCKER_CMD"
    return 0
}

# Function to check container status
check_container_status() {
    local service_name=$1
    local container_name=$2
    
    log_step "Checking $service_name..."
    
    # Check if container exists and is running
    if $DOCKER_CMD -f $COMPOSE_FILE ps -q $service_name > /dev/null 2>&1; then
        local status=$($DOCKER_CMD -f $COMPOSE_FILE ps --format "table {{.Status}}" $service_name | tail -n 1)
        
        if [[ $status == *"Up"* ]] && [[ $status == *"healthy"* ]]; then
            log_success "$service_name is running and healthy"
            return 0
        elif [[ $status == *"Up"* ]]; then
            log_warning "$service_name is running but health check may be failing"
            
            # Show recent logs for debugging
            echo "Recent logs:"
            $DOCKER_CMD -f $COMPOSE_FILE logs --tail=5 $service_name 2>/dev/null || echo "No logs available"
            return 1
        else
            log_error "$service_name is not running properly. Status: $status"
            
            # Show recent logs for debugging
            echo "Recent logs:"
            $DOCKER_CMD -f $COMPOSE_FILE logs --tail=10 $service_name 2>/dev/null || echo "No logs available"
            return 1
        fi
    else
        log_error "$service_name container not found"
        return 1
    fi
}

# Function to check specific service connectivity
check_service_connectivity() {
    log_step "Testing service connectivity..."
    
    # Test Redis
    if check_container_status "redis" "redis"; then
        if $DOCKER_CMD -f $COMPOSE_FILE exec -T redis redis-cli ping 2>/dev/null | grep -q "PONG"; then
            log_success "Redis connectivity test passed"
        else
            log_warning "Redis connectivity test failed"
        fi
    fi
    
    # Test Neo4j
    if check_container_status "neo4j" "neo4j"; then
        log_info "Neo4j web interface should be available at http://localhost:7474"
    fi
    
    # Test Zookeeper
    if check_container_status "zookeeper" "zookeeper"; then
        if $DOCKER_CMD -f $COMPOSE_FILE exec -T zookeeper bash -c "echo 'ruok' | nc -w 2 localhost 2181" 2>/dev/null | grep -q "imok"; then
            log_success "Zookeeper connectivity test passed"
        else
            log_warning "Zookeeper connectivity test failed"
        fi
    fi
    
    # Test Kafka
    if check_container_status "kafka" "kafka"; then
        if $DOCKER_CMD -f $COMPOSE_FILE exec -T kafka kafka-topics.sh --bootstrap-server localhost:9092 --list > /dev/null 2>&1; then
            log_success "Kafka connectivity test passed"
        else
            log_warning "Kafka connectivity test failed"
        fi
    fi
}

# Function to provide troubleshooting suggestions
provide_troubleshooting() {
    echo ""
    log_info "=== TROUBLESHOOTING SUGGESTIONS ==="
    echo ""
    
    log_info "For Zookeeper issues:"
    echo "  • Check if port 2181 is available"
    echo "  • Verify Zookeeper logs: $DOCKER_CMD -f $COMPOSE_FILE logs zookeeper"
    echo "  • Test manually: echo 'ruok' | nc localhost 2181"
    echo ""
    
    log_info "For Kafka issues:"
    echo "  • Ensure Zookeeper is healthy first"
    echo "  • Check Kafka logs: $DOCKER_CMD -f $COMPOSE_FILE logs kafka"
    echo "  • Verify ports 9092 and 29092 are available"
    echo "  • Test manually: $DOCKER_CMD -f $COMPOSE_FILE exec kafka kafka-topics.sh --bootstrap-server localhost:9092 --list"
    echo ""
    
    log_info "For Spark issues:"
    echo "  • Ensure Kafka is healthy first"
    echo "  • Check Spark logs: $DOCKER_CMD -f $COMPOSE_FILE logs spark-master"
    echo "  • Verify port 8080 is available for Spark UI"
    echo ""
    
    log_info "To restart specific services:"
    echo "  • Restart Zookeeper: $DOCKER_CMD -f $COMPOSE_FILE restart zookeeper"
    echo "  • Restart Kafka: $DOCKER_CMD -f $COMPOSE_FILE restart kafka"
    echo "  • Restart all: $DOCKER_CMD -f $COMPOSE_FILE restart"
    echo ""
    
    log_info "To check resource usage:"
    echo "  • Docker stats: $DOCKER_CMD -f $COMPOSE_FILE top"
    echo "  • System resources: docker system df"
}

# Main execution
main() {
    echo ""
    log_info "=== SERVICE HEALTH CHECK ==="
    echo ""
    
    # Check Docker
    if ! check_docker; then
        exit 1
    fi
    
    echo ""
    log_info "=== CONTAINER STATUS ==="
    
    # Define services in dependency order
    declare -a services=(
        "redis:redis"
        "neo4j:neo4j"
        "zookeeper:zookeeper"
        "kafka:kafka"
        "spark-master:spark-master"
        "spark-worker:spark-worker"
        "llm-service:llm-service"
        "streamlit-app:streamlit-app"
    )
    
    local all_healthy=true
    
    # Check each service
    for service_info in "${services[@]}"; do
        IFS=':' read -r service container <<< "$service_info"
        if ! check_container_status "$service" "$container"; then
            all_healthy=false
        fi
        echo ""
    done
    
    # Test connectivity
    echo ""
    log_info "=== CONNECTIVITY TESTS ==="
    check_service_connectivity
    
    # Summary
    echo ""
    if $all_healthy; then
        log_success "=== ALL SERVICES HEALTHY ==="
        log_info "Dashboard should be available at http://localhost:8501"
    else
        log_warning "=== SOME SERVICES NEED ATTENTION ==="
        provide_troubleshooting
    fi
    
    echo ""
}

# Run the main function
main "$@"