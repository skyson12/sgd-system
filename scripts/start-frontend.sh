#!/bin/bash

# Start Frontend Development Server
set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_status "Starting SGD Frontend Development Server..."

# Check if we're in the right directory
if [ ! -f "frontend/package.json" ]; then
    echo "Error: Please run this script from the SGD project root directory"
    exit 1
fi

# Navigate to frontend directory
cd frontend

# Install dependencies if node_modules doesn't exist
if [ ! -d "node_modules" ]; then
    print_status "Installing frontend dependencies..."
    npm install
fi

# Start the development server
print_status "Starting Next.js development server..."
print_success "Frontend will be available at: http://localhost:3000"
print_status "Press Ctrl+C to stop the server"

npm run dev