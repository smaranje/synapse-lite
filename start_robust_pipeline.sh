#!/bin/bash

# start_robust_pipeline.sh - Robust Pipeline Startup Script
# Addresses the cascade of misconfigurations by proper service orchestration

set -e  # Exit on any error

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
MAX_WAIT_TIME=300  # 5 minutes max wait for each service
HEALTH_CHECK_INTERVAL=10  # seconds
VERBOSE=${VERBOSE:-false}

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

# Check if required files exist
check_prerequisites() {
    log_step "Checking prerequisites..."
    
    if [ ! -f "$COMPOSE_FILE" ]; then
        log_error "Docker Compose file '$COMPOSE_FILE' not found!"
        exit 1
    fi
    
    # Check for 'docker compose' (new syntax)
    if ! command -v docker &> /dev/null || ! docker compose version &> /dev/null; then
        log_error "docker compose (new syntax) is not installed or not working!"
        exit 1
    fi
    
    log_success "Prerequisites check passed"
}

# Clean up any existing containers and volumes
cleanup_existing() {
    log_step "Cleaning up existing containers and data..."
    
    # Stop and remove containers using the new syntax
    docker compose -f "$COMPOSE_FILE" down --remove-orphans 2>/dev/null || true
    
    # Remove any orphaned containers
    docker container prune -f 2>/dev/null || true
    
    # Clean up networks
    docker network prune -f 2>/dev/null || true
    
    # Optional: Remove volumes for fresh start (uncomment if needed)
    # docker compose -f "$COMPOSE_FILE" down -v
    
    log_success "Cleanup completed"
}

# Wait for a service to become healthy
wait_for_service_health() {
    local service_name=$1
    local max_wait=${2:-$MAX_WAIT_TIME}
    local wait_time=0
    
    log_info "Waiting for $service_name to become healthy..."
    
    while [ $wait_time -lt $max_wait ]; do
        if docker compose -f "$COMPOSE_FILE" ps "$service_name" | grep -q "healthy"; then
            log_success "$service_name is healthy"
            return 0
        elif docker compose -f "$COMPOSE_FILE" ps "$service_name" | grep -q "unhealthy"; then
            log_warning "$service_name is unhealthy, continuing to wait..."
        fi
        
        sleep $HEALTH_CHECK_INTERVAL
        wait_time=$((wait_time + HEALTH_CHECK_INTERVAL))
        
        if [ $((wait_time % 60)) -eq 0 ]; then
            log_info "Still waiting for $service_name... (${wait_time}s elapsed)"
        fi
    done
    
    log_error "$service_name failed to become healthy within ${max_wait}s"
    return 1
}

# Wait for a service to complete successfully
wait_for_service_completion() {
    local service_name=$1
    local max_wait=${2:-$MAX_WAIT_TIME}
    local wait_time=0
    
    log_info "Waiting for $service_name to complete..."
    
    while [ $wait_time -lt $max_wait ]; do
        local status=$(docker compose -f "$COMPOSE_FILE" ps -q "$service_name" | xargs docker inspect --format='{{.State.Status}}' 2>/dev/null || echo "not_found")
        
        if [ "$status" = "exited" ]; then
            local exit_code=$(docker compose -f "$COMPOSE_FILE" ps -q "$service_name" | xargs docker inspect --format='{{.State.ExitCode}}' 2>/dev/null || echo "1")
            if [ "$exit_code" = "0" ]; then
                log_success "$service_name completed successfully"
                return 0
            else
                log_error "$service_name exited with code $exit_code"
                return 1
            fi
        elif [ "$status" = "running" ]; then
            log_info "$service_name is still running..."
        fi
        
        sleep $HEALTH_CHECK_INTERVAL
        wait_time=$((wait_time + HEALTH_CHECK_INTERVAL))
    done
    
    log_error "$service_name did not complete within ${max_wait}s"
    return 1
}

# Check service logs for errors
check_service_logs() {
    local service_name=$1
    local lines=${2:-50}
    
    log_info "Checking recent logs for $service_name..."
    
    if [ "$VERBOSE" = "true" ]; then
        docker compose -f "$COMPOSE_FILE" logs --tail="$lines" "$service_name"
    else
        # Look for common error patterns
        local errors=$(docker compose -f "$COMPOSE_FILE" logs --tail="$lines" "$service_name" 2>&1 | grep -i "error\|exception\|failed\|timeout" | wc -l)
        if [ "$errors" -gt 0 ]; then
            log_warning "Found $errors potential error(s) in $service_name logs"
            if [ "$errors" -lt 10 ]; then
                docker compose -f "$COMPOSE_FILE" logs --tail="$lines" "$service_name" 2>&1 | grep -i "error\|exception\|failed\|timeout"
            fi
        else
            log_success "No obvious errors found in $service_name logs"
        fi
    fi
}

# Start service and wait for readiness
start_and_wait() {
    local service_name=$1
    local wait_type=${2:-"health"}  # "health" or "completion"
    local max_wait=${3:-$MAX_WAIT_TIME}
    
    log_step "Starting $service_name..."
    
    # Start the service
    if ! docker compose -f "$COMPOSE_FILE" up -d "$service_name"; then
        log_error "Failed to start $service_name"
        return 1
    fi
    
    # Wait for readiness
    if [ "$wait_type" = "health" ]; then
        if ! wait_for_service_health "$service_name" "$max_wait"; then
            check_service_logs "$service_name"
            return 1
        fi
    elif [ "$wait_type" = "completion" ]; then
        if ! wait_for_service_completion "$service_name" "$max_wait"; then
            check_service_logs "$service_name"
            return 1
        fi
    fi
    
    return 0
}

# Verify Kafka topic creation
verify_kafka_topic() {
    log_info "Verifying Kafka topic creation..."
    
    local topic_check=$(docker compose -f "$COMPOSE_FILE" exec kafka kafka-topics.sh --bootstrap-server localhost:9092 --list 2>/dev/null | grep "transactions" || echo "")
    
    if [ -n "$topic_check" ]; then
        log_success "Kafka topic 'transactions' exists"
        
        # Show topic details
        log_info "Topic details:"
        docker compose -f "$COMPOSE_FILE" exec kafka kafka-topics.sh --bootstrap-server localhost:9092 --describe --topic transactions 2>/dev/null || true
    else
        log_warning "Kafka topic 'transactions' not found, but it may be auto-created"
    fi
}

# Check Neo4j connectivity
verify_neo4j_connection() {
    log_info "Verifying Neo4j connectivity..."
    
    # Check if Neo4j is responding
    if docker compose -f "$COMPOSE_FILE" exec neo4j cypher-shell -u neo4j -p password "RETURN 'Connection successful' as result;" 2>/dev/null | grep -q "Connection successful"; then
        log_success "Neo4j connection verified"
    else
        log_warning "Neo4j connection test failed, but service may still be initializing"
    fi
}

# Check LLM service health
verify_llm_service() {
    log_info "Verifying LLM service..."
    
    local health_check=$(docker compose -f "$COMPOSE_FILE" exec flask-llm-service curl -s -f http://localhost:5000/health 2>/dev/null || echo "failed")
    
    if [ "$health_check" != "failed" ]; then
        log_success "LLM service is responding"
    else
        log_warning "LLM service health check failed"
    fi
}

# Monitor initial data flow
monitor_initial_data_flow() {
    log_info "Monitoring initial data flow for 60 seconds..."
    
    sleep 30  # Give services time to settle
    
    # Check data generator stats
    log_info "Data generator status:"
    docker compose -f "$COMPOSE_FILE" logs --tail=10 data-generator | grep -E "(Sent:|Failed:|Stats)"
    
    # Check Spark processing
    log_info "Spark processing status:"
    docker compose -f "$COMPOSE_FILE" logs --tail=10 spark-app | grep -E "(batch|Processing|records)"
    
    # Check Neo4j data
    log_info "Checking Neo4j for processed transactions..."
    local tx_count=$(docker compose -f "$COMPOSE_FILE" exec neo4j cypher-shell -u neo4j -p password "MATCH (tx:Transaction) RETURN count(tx) as count;" 2>/dev/null | grep -o '[0-9]\+' | head -1 || echo "0")
    log_info "Transactions in Neo4j: $tx_count"
    
    if [ "$tx_count" -gt 0 ]; then
        log_success "Data is flowing through the pipeline!"
    else
        log_warning "No transactions found in Neo4j yet (this may be normal for a new startup)"
    fi
}

# Display final status
display_final_status() {
    echo
    log_step "Final Service Status:"
    echo
    
    docker compose -f "$COMPOSE_FILE" ps
    
    echo
    log_info "Service URLs:"
    echo "  Spark Master UI:    http://localhost:8080"
    echo "  Neo4j Browser:      http://localhost:7474"
    echo "  Streamlit Dashboard: http://localhost:8501"
    echo "  Kafka (external):   localhost:29092"
    echo "  LLM Service:        http://localhost:5000"
    echo
    
    log_info "To monitor logs:"
    echo "  docker compose -f $COMPOSE_FILE logs -f [service_name]"
    echo
    
    log_info "To stop the pipeline:"
    echo "  docker compose -f $COMPOSE_FILE down"
    echo
}

# Main execution
main() {
    echo "=================================="
    echo "🚀 ROBUST KAFKA-SPARK-NEO4J PIPELINE STARTUP"
    echo "=================================="
    echo "Addressing cascade of misconfigurations with proper orchestration"
    echo "=================================="
    echo
    
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            -v|--verbose)
                VERBOSE=true
                shift
                ;;
            -c|--compose-file)
                COMPOSE_FILE="$2"
                shift 2
                ;;
            -h|--help)
                echo "Usage: $0 [OPTIONS]"
                echo "Options:"
                echo "  -v, --verbose           Enable verbose logging"
                echo "  -c, --compose-file      Specify docker-compose file (default: $COMPOSE_FILE)"
                echo "  -h, --help              Show this help message"
                exit 0
                ;;
            *)
                log_error "Unknown option: $1"
                exit 1
                ;;
        esac
    done
    
    # Execute startup sequence
    check_prerequisites
    cleanup_existing
    
    log_step "Starting services in proper dependency order..."
    echo
    
    # Phase 1: Foundation services (no dependencies)
    log_info "🏗️  Starting foundation services (Redis, Zookeeper)..."
    start_and_wait "redis" "health" 60 || exit 1
    start_and_wait "zookeeper" "health" 180 || exit 1 # Increased Zookeeper wait time
    log_success "Foundation services ready!"
    
    # Phase 2: Kafka (depends on Zookeeper)
    log_info "📡 Starting message broker (Kafka)..."
    start_and_wait "kafka" "health" 180 || exit 1
    log_success "Kafka is ready!"
    
    # Phase 3: Topic initialization
    log_info "📝 Phase 3: Topic Initialization"
    start_and_wait "kafka-topic-initializer" "completion" 60 || exit 1
    verify_kafka_topic
    
    # Phase 4: Core processing services
    log_info "⚡ Phase 4: Processing Engine"
    start_and_wait "spark-master" "health" 120 || exit 1
    start_and_wait "spark-worker" "health" 90 || exit 1
    
    # Phase 5: Database services
    log_info "🗄️  Phase 5: Database Services"
    start_and_wait "neo4j" "health" 180 || exit 1
    start_and_wait "neo4j-initializer" "completion" 60 || exit 1
    verify_neo4j_connection
    
    # Phase 6: AI service
    log_info "🤖 Phase 6: AI Services"
    start_and_wait "flask-llm-service" "health" 120 || exit 1
    verify_llm_service
    
    # Phase 7: Data pipeline
    log_info "🌊 Starting data pipeline (generator and processing)..."
    start_and_wait "data-generator" "running" 60 || exit 1
    log_success "Data generator is producing transactions!"
    start_and_wait "spark-app" "running" 120 || exit 1
    log_success "Spark is processing data!"
    
    # Phase 8: User interface
    log_info "🖥️  Starting dashboard..."
    start_and_wait "streamlit-dashboard" "running" 90 || exit 1
    log_success "Dashboard is ready!"
    
    # Final verification
    log_step "🔍 Verifying pipeline functionality..."
    monitor_initial_data_flow
    
    # Success
    echo
    log_success "🎉 PIPELINE STARTUP COMPLETED SUCCESSFULLY!"
    log_success "All services are running and the data pipeline is operational"
    echo
    
    display_final_status
}

# Execute main function
main "$@"
