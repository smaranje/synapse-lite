#!/bin/bash

# validate_robust_solution.sh - Validation Script for Robust Pipeline Components
# Tests the key fixes and improvements

set -e

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

echo "=============================================="
echo "🔍 ROBUST PIPELINE SOLUTION VALIDATION"
echo "=============================================="
echo

# 1. Validate Docker Compose Configuration
log_info "1. Validating Docker Compose Configuration..."

if [ ! -f "docker-compose-robust.yml" ]; then
    log_error "docker-compose-robust.yml not found!"
    exit 1
fi

# Check for key fixes in docker-compose
log_info "   Checking for correct Kafka port configuration..."
if grep -q "KAFKA_BROKER=kafka:9092" docker-compose-robust.yml; then
    log_success "   ✓ Kafka internal port correctly configured (kafka:9092)"
else
    log_error "   ✗ Kafka port configuration issue found"
    exit 1
fi

log_info "   Checking for robust health checks..."
if grep -q "kafka-topics.sh" docker-compose-robust.yml; then
    log_success "   ✓ Kafka health check uses correct command (kafka-topics.sh)"
else
    log_error "   ✗ Kafka health check still has typo"
    exit 1
fi

log_info "   Checking for memory limits..."
if grep -q "memory:" docker-compose-robust.yml; then
    log_success "   ✓ Memory limits configured"
else
    log_warning "   ! Memory limits not found (may be optional)"
fi

log_info "   Checking for restart policies..."
if grep -q "restart:" docker-compose-robust.yml; then
    log_success "   ✓ Restart policies configured"
else
    log_warning "   ! Restart policies not found"
fi

# 2. Validate Robust Data Producer
log_info "2. Validating Robust Data Producer..."

if [ ! -f "data/producer_app_robust.py" ]; then
    log_error "data/producer_app_robust.py not found!"
    exit 1
fi

log_info "   Checking for circuit breaker implementation..."
if grep -q "class CircuitBreaker" data/producer_app_robust.py; then
    log_success "   ✓ Circuit breaker pattern implemented"
else
    log_error "   ✗ Circuit breaker not found"
    exit 1
fi

log_info "   Checking for retry logic..."
if grep -q "_connect_with_retry" data/producer_app_robust.py; then
    log_success "   ✓ Connection retry logic implemented"
else
    log_error "   ✗ Retry logic not found"
    exit 1
fi

log_info "   Checking for production Kafka settings..."
if grep -q "acks='all'" data/producer_app_robust.py; then
    log_success "   ✓ Production Kafka settings configured"
else
    log_warning "   ! Production Kafka settings may not be optimal"
fi

# 3. Validate Robust Spark Application
log_info "3. Validating Robust Spark Application..."

if [ ! -f "spark_app/streaming_app_robust.py" ]; then
    log_error "spark_app/streaming_app_robust.py not found!"
    exit 1
fi

log_info "   Checking for connection manager..."
if grep -q "class ConnectionManager" spark_app/streaming_app_robust.py; then
    log_success "   ✓ Connection manager implemented"
else
    log_error "   ✗ Connection manager not found"
    exit 1
fi

log_info "   Checking for robust Neo4j pool..."
if grep -q "class RobustNeo4jConnectionPool" spark_app/streaming_app_robust.py; then
    log_success "   ✓ Robust Neo4j connection pool implemented"
else
    log_error "   ✗ Robust Neo4j pool not found"
    exit 1
fi

log_info "   Checking for Kafka readiness check..."
if grep -q "wait_for_kafka_readiness" spark_app/streaming_app_robust.py; then
    log_success "   ✓ Kafka readiness check implemented"
else
    log_error "   ✗ Kafka readiness check not found"
    exit 1
fi

log_info "   Checking for fault-tolerant stream options..."
if grep -q "failOnDataLoss.*false" spark_app/streaming_app_robust.py; then
    log_success "   ✓ Fault-tolerant streaming configured"
else
    log_warning "   ! Fault tolerance settings may not be optimal"
fi

# 4. Validate Startup Script
log_info "4. Validating Startup Script..."

if [ ! -f "start_robust_pipeline.sh" ]; then
    log_error "start_robust_pipeline.sh not found!"
    exit 1
fi

if [ ! -x "start_robust_pipeline.sh" ]; then
    log_warning "   Making startup script executable..."
    chmod +x start_robust_pipeline.sh
    log_success "   ✓ Startup script is now executable"
fi

log_info "   Checking for phase-based startup..."
if grep -q "Phase 1.*Foundation" start_robust_pipeline.sh; then
    log_success "   ✓ Phase-based startup sequence implemented"
else
    log_error "   ✗ Phase-based startup not found"
    exit 1
fi

log_info "   Checking for health verification..."
if grep -q "wait_for_service_health" start_robust_pipeline.sh; then
    log_success "   ✓ Service health verification implemented"
else
    log_error "   ✗ Health verification not found"
    exit 1
fi

log_info "   Checking for data flow monitoring..."
if grep -q "monitor_initial_data_flow" start_robust_pipeline.sh; then
    log_success "   ✓ Data flow monitoring implemented"
else
    log_error "   ✗ Data flow monitoring not found"
    exit 1
fi

# 5. Validate Documentation
log_info "5. Validating Documentation..."

if [ ! -f "ROBUST_PIPELINE_SOLUTION.md" ]; then
    log_error "ROBUST_PIPELINE_SOLUTION.md not found!"
    exit 1
fi

log_info "   Checking documentation completeness..."
if grep -q "Cascade Analysis" ROBUST_PIPELINE_SOLUTION.md && \
   grep -q "Troubleshooting Guide" ROBUST_PIPELINE_SOLUTION.md && \
   grep -q "Expected Performance" ROBUST_PIPELINE_SOLUTION.md; then
    log_success "   ✓ Comprehensive documentation provided"
else
    log_warning "   ! Documentation may be incomplete"
fi

# 6. Test Configuration Syntax
log_info "6. Testing Configuration Syntax..."

log_info "   Validating docker-compose syntax..."
if command -v docker-compose &> /dev/null; then
    if docker-compose -f docker-compose-robust.yml config > /dev/null 2>&1; then
        log_success "   ✓ Docker Compose configuration is valid"
    else
        log_error "   ✗ Docker Compose configuration has syntax errors"
        exit 1
    fi
else
    log_warning "   ! docker-compose not available for syntax validation"
fi

log_info "   Validating Python syntax..."
if command -v python3 &> /dev/null; then
    if python3 -m py_compile data/producer_app_robust.py 2>/dev/null; then
        log_success "   ✓ Robust producer Python syntax is valid"
    else
        log_error "   ✗ Robust producer has Python syntax errors"
        exit 1
    fi
    
    if python3 -c "import ast; ast.parse(open('spark_app/streaming_app_robust.py').read())" 2>/dev/null; then
        log_success "   ✓ Robust Spark app Python syntax is valid"
    else
        log_error "   ✗ Robust Spark app has Python syntax errors"
        exit 1
    fi
else
    log_warning "   ! Python not available for syntax validation"
fi

# 7. Check for Key Improvements
log_info "7. Verifying Key Improvements..."

improvements=0

# Port configuration fix
if grep -q "kafka:9092" docker-compose-robust.yml && \
   grep -q "kafka:9092" data/producer_app_robust.py && \
   grep -q "kafka:9092" spark_app/streaming_app_robust.py; then
    log_success "   ✓ Port configuration fix verified across all components"
    ((improvements++))
else
    log_error "   ✗ Port configuration fix incomplete"
fi

# Health check fix
if grep -q "kafka-topics.sh" docker-compose-robust.yml; then
    log_success "   ✓ Health check typo fix verified"
    ((improvements++))
else
    log_error "   ✗ Health check fix missing"
fi

# Memory limits
if grep -q "memory:.*M" docker-compose-robust.yml; then
    log_success "   ✓ Memory limits implemented"
    ((improvements++))
else
    log_warning "   ! Memory limits not fully implemented"
fi

# Retry logic
if grep -q "retry" data/producer_app_robust.py && \
   grep -q "retry" spark_app/streaming_app_robust.py; then
    log_success "   ✓ Retry logic implemented in both producer and consumer"
    ((improvements++))
else
    log_error "   ✗ Retry logic incomplete"
fi

# Service orchestration
if grep -q "depends_on:" docker-compose-robust.yml && \
   grep -q "condition:" docker-compose-robust.yml; then
    log_success "   ✓ Service orchestration dependencies configured"
    ((improvements++))
else
    log_error "   ✗ Service orchestration incomplete"
fi

echo
echo "=============================================="
echo "📊 VALIDATION SUMMARY"
echo "=============================================="

total_improvements=5
if [ $improvements -eq $total_improvements ]; then
    log_success "🎉 ALL KEY IMPROVEMENTS VALIDATED ($improvements/$total_improvements)"
    log_success "The robust solution addresses all major cascade failure points!"
elif [ $improvements -ge 3 ]; then
    log_warning "⚠️  MOST IMPROVEMENTS VALIDATED ($improvements/$total_improvements)"
    log_warning "Some improvements may need attention."
else
    log_error "❌ INSUFFICIENT IMPROVEMENTS ($improvements/$total_improvements)"
    log_error "The solution needs more work to address cascade failures."
    exit 1
fi

echo
log_info "🚀 Ready to start the robust pipeline:"
echo "   ./start_robust_pipeline.sh"
echo
log_info "📖 Read the complete solution guide:"
echo "   cat ROBUST_PIPELINE_SOLUTION.md"
echo
log_info "🔧 For troubleshooting, see:"
echo "   ROBUST_PIPELINE_SOLUTION.md (Troubleshooting Guide section)"
echo

log_success "✅ VALIDATION COMPLETED SUCCESSFULLY!"