#!/bin/bash
# Quick Backend Test Script
# This script helps you verify the backend setup and run basic tests

set -e  # Exit on error

echo "🚀 Data Extraction Backend - Quick Test"
echo "========================================"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Helper functions
print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_step() {
    echo -e "\n${YELLOW}→${NC} $1"
}

# 1. Check Python version
print_step "Checking Python version..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    print_success "Python found: $PYTHON_VERSION"
    PYTHON_CMD=python3
elif command -v python &> /dev/null; then
    PYTHON_VERSION=$(python --version)
    print_success "Python found: $PYTHON_VERSION"
    PYTHON_CMD=python
else
    print_error "Python not found. Please install Python 3.11+"
    exit 1
fi

# 2. Check if we're in the right directory
print_step "Checking directory..."
if [ -f "src/main.py" ]; then
    print_success "Found src/main.py - in correct directory"
else
    print_error "Not in backend directory. Please cd to /home/noahdarwich/code/coderAI/backend"
    exit 1
fi

# 3. Check/create virtual environment
print_step "Checking virtual environment..."
if [ -d "venv" ]; then
    print_success "Virtual environment exists"
else
    print_warning "Creating virtual environment..."
    $PYTHON_CMD -m venv venv
    print_success "Virtual environment created"
fi

# 4. Activate virtual environment
print_step "Activating virtual environment..."
source venv/bin/activate || {
    print_error "Failed to activate virtual environment"
    exit 1
}
print_success "Virtual environment activated"

# 5. Install dependencies
print_step "Installing dependencies..."
pip install -q --upgrade pip
if pip install -q -r requirements.txt; then
    print_success "Dependencies installed"
else
    print_error "Failed to install dependencies"
    exit 1
fi

# 6. Check environment variables
print_step "Checking environment variables..."
if [ -f ".env" ]; then
    print_success "Found .env file"
else
    print_warning ".env file not found. Creating from .env.example..."
    cp .env.example .env
    print_warning "Please edit .env file with your configuration:"
    print_warning "  - DATABASE_URL"
    print_warning "  - OPENAI_API_KEY"
    echo ""
    read -p "Press Enter to open .env in nano (or Ctrl+C to exit and edit manually)..."
    nano .env
fi

# 7. Check PostgreSQL
print_step "Checking PostgreSQL..."
if command -v psql &> /dev/null; then
    print_success "PostgreSQL client found"

    # Try to connect
    if psql --version &> /dev/null; then
        print_success "PostgreSQL is available"
    fi
else
    print_warning "PostgreSQL client not found - you may need to install it"
    print_warning "  Ubuntu/Debian: sudo apt-get install postgresql-client"
    print_warning "  macOS: brew install postgresql"
fi

# 8. Test Python imports
print_step "Testing Python imports..."
if $PYTHON_CMD -c "from src.main import app" 2>/dev/null; then
    print_success "All Python imports working"
else
    print_error "Import error - check dependencies"
    $PYTHON_CMD -c "from src.main import app"
    exit 1
fi

# 9. Summary
echo ""
echo "========================================"
echo "✅ Quick test complete!"
echo ""
echo "Next steps:"
echo "1. Ensure PostgreSQL is running and .env is configured"
echo "2. Run migrations: alembic upgrade head"
echo "3. Start server: uvicorn src.main:app --reload"
echo "4. Open API docs: http://localhost:8000/docs"
echo ""
echo "For detailed testing instructions, see TESTING_GUIDE.md"
echo "========================================"
