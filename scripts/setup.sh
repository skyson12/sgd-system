#!/bin/bash

# SGD System Setup Script
set -e

echo "🚀 Starting SGD System Setup..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if .env file exists
if [ ! -f ".env" ]; then
    print_warning ".env file not found. Creating from template..."
    cp .env.template .env
    print_warning "Please edit .env file with your configuration before continuing."
    exit 1
fi

# Load environment variables
set -a
source .env
set +a

print_status "Environment variables loaded"

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
print_status "Checking prerequisites..."

if ! command_exists docker; then
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command_exists docker-compose; then
    print_error "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

if ! command_exists node; then
    print_error "Node.js is not installed. Please install Node.js first."
    exit 1
fi

if ! command_exists python3; then
    print_error "Python 3 is not installed. Please install Python 3 first."
    exit 1
fi

print_success "All prerequisites are installed"

# Create necessary directories
print_status "Creating necessary directories..."
mkdir -p logs
mkdir -p uploads
mkdir -p backups
mkdir -p data/{postgres,minio,weaviate,keycloak,n8n,redis}

print_success "Directories created"

# Build and start services
print_status "Building and starting Docker services..."

# Stop any existing services
docker-compose down

# Build services
docker-compose build

# Start infrastructure services first
print_status "Starting infrastructure services..."
docker-compose up -d postgres redis minio weaviate keycloak

# Wait for services to be ready
print_status "Waiting for infrastructure services to be ready..."
sleep 30

# Check service health
check_service_health() {
    local service=$1
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if docker-compose ps $service | grep -q "healthy\|running"; then
            print_success "$service is ready"
            return 0
        fi
        
        print_status "Waiting for $service... (attempt $attempt/$max_attempts)"
        sleep 5
        attempt=$((attempt + 1))
    done
    
    print_error "$service failed to become ready"
    return 1
}

# Check infrastructure services
check_service_health postgres
check_service_health redis  
check_service_health minio
check_service_health weaviate
check_service_health keycloak

# Start n8n
print_status "Starting n8n..."
docker-compose up -d n8n
sleep 10
check_service_health n8n

# Start application services
print_status "Starting application services..."
docker-compose up -d api-service ai-service audit-service
sleep 20

check_service_health api-service
check_service_health ai-service
check_service_health audit-service

print_success "All services are running!"

# Display service URLs
print_status "Service URLs:"
echo "  📱 Frontend: http://localhost:3000 (run ./scripts/start-frontend.sh)"
echo "  🔧 API Documentation: http://localhost:8000/docs"
echo "  🤖 AI Service: http://localhost:8001/docs"
echo "  📊 Audit Service: http://localhost:8002/docs"
echo "  🔐 Keycloak Admin: http://localhost:8090 (admin/admin_password)"
echo "  🗄️ MinIO Console: http://localhost:9001 (sgd_minio/sgd_minio_password)"
echo "  🔄 n8n: http://localhost:5678 (admin/admin_password)"
echo "  🔍 Weaviate: http://localhost:8080"

# Run smoke tests
print_status "Running smoke tests..."
./scripts/smoke-test.sh

print_success "🎉 SGD System setup completed successfully!"
print_status "Next steps:"
echo "  0. Start the frontend: ./scripts/start-frontend.sh"
echo "  1. Configure Google AppSheet integration"
echo "  2. Set up n8n workflows"
echo "  3. Configure Keycloak realm and clients"
echo "  4. Test document upload and processing"

print_status "For detailed instructions, see DEPLOYMENT.md"