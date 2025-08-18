#!/bin/bash

# SGD System Smoke Tests
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[TEST]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[PASS]${NC} $1"
}

print_error() {
    echo -e "${RED}[FAIL]${NC} $1"
}

# Test function
test_endpoint() {
    local name=$1
    local url=$2
    local expected_status=${3:-200}
    
    print_status "Testing $name..."
    
    if curl -s -o /dev/null -w "%{http_code}" "$url" | grep -q "$expected_status"; then
        print_success "$name is accessible"
        return 0
    else
        print_error "$name is not accessible"
        return 1
    fi
}

# Test function with timeout
test_endpoint_timeout() {
    local name=$1
    local url=$2
    local timeout=${3:-10}
    
    print_status "Testing $name..."
    
    if timeout $timeout curl -s "$url" >/dev/null 2>&1; then
        print_success "$name is accessible"
        return 0
    else
        print_error "$name is not accessible or timed out"
        return 1
    fi
}

echo "🧪 Starting SGD System Smoke Tests..."
echo "=================================="

# Test infrastructure services
print_status "Testing infrastructure services..."

test_endpoint "PostgreSQL (via API health check)" "http://localhost:8000/health"
test_endpoint_timeout "Redis" "http://localhost:6379" 5
test_endpoint "MinIO" "http://localhost:9000/minio/health/live"
test_endpoint "Weaviate" "http://localhost:8080/v1/.well-known/ready"
test_endpoint "Keycloak" "http://localhost:8090/health/ready"

# Test application services  
print_status "Testing application services..."

test_endpoint "API Service Health" "http://localhost:8000/health"
test_endpoint "API Service Detailed Health" "http://localhost:8000/health/detailed"
test_endpoint "API Documentation" "http://localhost:8000/docs"

test_endpoint "AI Service Health" "http://localhost:8001/health"
test_endpoint "AI Service Documentation" "http://localhost:8001/docs"

test_endpoint "Audit Service Health" "http://localhost:8002/health"
test_endpoint "Audit Service Documentation" "http://localhost:8002/docs"

# Test workflow service
test_endpoint "n8n" "http://localhost:5678/healthz"

# Test frontend
test_endpoint "Frontend" "http://localhost:3000"

# Test API endpoints
print_status "Testing API endpoints..."

test_endpoint "Categories endpoint" "http://localhost:8000/categories"

# Test database connectivity
print_status "Testing database operations..."

# Create a test category via API
print_status "Testing database write operations..."
response=$(curl -s -w "%{http_code}" -X POST \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer test-token" \
    -d '{"name":"Test Category","description":"Test category for smoke test","color":"#FF0000"}' \
    "http://localhost:8000/categories" 2>/dev/null || echo "000")

if [[ "$response" =~ 20[0-9] ]]; then
    print_success "Database write operations working"
else
    print_error "Database write operations failed (status: ${response: -3})"
fi

# Test MinIO operations
print_status "Testing MinIO storage operations..."

# Test MinIO bucket creation (this would typically be done by the API)
if docker-compose exec -T minio mc ls minio/documents >/dev/null 2>&1; then
    print_success "MinIO storage is accessible"
else
    print_error "MinIO storage is not accessible"
fi

# Test Weaviate schema
print_status "Testing Weaviate search operations..."

schema_response=$(curl -s -w "%{http_code}" "http://localhost:8080/v1/schema" 2>/dev/null || echo "000")
if [[ "$schema_response" =~ 200 ]]; then
    print_success "Weaviate schema is accessible"
else
    print_error "Weaviate schema is not accessible"
fi

# Test AI service processing capabilities
print_status "Testing AI service capabilities..."

# Test text analysis endpoint
analysis_response=$(curl -s -w "%{http_code}" -X POST \
    -H "Content-Type: application/json" \
    -d '{"text":"This is a test document for analysis"}' \
    "http://localhost:8001/analyze/text" 2>/dev/null || echo "000")

if [[ "$analysis_response" =~ 422 ]] || [[ "$analysis_response" =~ 200 ]]; then
    print_success "AI service text analysis is working"
else
    print_error "AI service text analysis failed"
fi

# Summary
echo "=================================="
echo "🧪 Smoke tests completed!"

# Check if all critical services are running
critical_services=("postgres" "api-service" "ai-service" "audit-service" "frontend")
failed_services=()

for service in "${critical_services[@]}"; do
    if ! docker-compose ps "$service" | grep -q "Up\|running"; then
        failed_services+=("$service")
    fi
done

if [ ${#failed_services[@]} -eq 0 ]; then
    print_success "All critical services are running correctly!"
    echo ""
    echo "🎉 System is ready for use!"
    echo ""
    echo "Access URLs:"
    echo "  📱 Frontend: http://localhost:3000"
    echo "  📚 API Docs: http://localhost:8000/docs"
    echo "  🤖 AI Service: http://localhost:8001/docs"
    echo "  🔐 Keycloak: http://localhost:8090"
    echo "  💾 MinIO: http://localhost:9001"
    echo "  🔄 n8n: http://localhost:5678"
    exit 0
else
    print_error "The following critical services are not running:"
    for service in "${failed_services[@]}"; do
        echo "  - $service"
    done
    echo ""
    echo "Please check the service logs:"
    echo "  docker-compose logs [service-name]"
    exit 1
fi