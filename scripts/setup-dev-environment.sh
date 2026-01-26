#!/bin/bash
# QFZZ Development Environment Setup
set -e

echo "🚀 Setting up QFZZ development environment..."

# Check Python version
python_version=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
if [[ "$python_version" < "3.10" ]]; then
    echo "❌ Error: Python 3.10+ required. Found: $python_version"
    exit 1
fi

echo "✓ Python version: $python_version"

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Install pre-commit
echo "🔧 Installing pre-commit..."
pip install pre-commit

# Install pre-commit hooks
echo "🪝 Setting up pre-commit hooks..."
pre-commit install

# Initialize detect-secrets baseline
echo "🔐 Initializing detect-secrets baseline..."
if [ ! -f .secrets.baseline ]; then
    detect-secrets scan > .secrets.baseline
    echo "✓ Created .secrets.baseline"
else
    echo "✓ .secrets.baseline already exists"
fi

# Create .env from example if needed
if [ ! -f .env ]; then
    echo "📝 Creating .env from .env.example..."
    cp .env.example .env
    echo "⚠️  Please edit .env with your actual API keys"
else
    echo "✓ .env already exists"
fi

# Run pre-commit on all files (first time setup)
echo "🧪 Running pre-commit checks on all files..."
pre-commit run --all-files || true

echo ""
echo "✅ Development environment setup complete!"
echo ""
echo "Next steps:"
echo "  1. Edit .env with your API keys"
echo "  2. Run tests: pytest"
echo "  3. Start coding! Pre-commit hooks will run automatically"
echo ""
