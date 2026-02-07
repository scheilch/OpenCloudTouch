#!/usr/bin/env bash
# Install Git Hooks for OpenCloudTouch
# This script configures pre-commit hooks for local development

set -e

echo "🔧 Installing Git Hooks for OpenCloudTouch..."
echo ""

# Check if in git repository
if [ ! -d ".git" ]; then
    echo "❌ Error: Not in a git repository root!"
    echo "   Run this script from the project root directory."
    exit 1
fi

# Check Python installation
echo "📦 Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "   ❌ Python not found! Install Python 3.11+ first."
    exit 1
fi
PYTHON_VERSION=$(python3 --version)
echo "   ✅ Found: $PYTHON_VERSION"

# Install pre-commit package
echo ""
echo "📦 Installing pre-commit framework..."
pip install pre-commit

# Install commitizen for commit message validation
echo ""
echo "📦 Installing commitizen..."
pip install commitizen

# Install backend dev dependencies
echo ""
echo "📦 Installing backend dev dependencies..."
pip install -r apps/backend/requirements-dev.txt || {
    echo "   ⚠️  Warning: Could not install backend dependencies"
}

# Check Node.js installation
echo ""
echo "📦 Checking Node.js installation..."
if ! command -v node &> /dev/null; then
    echo "   ❌ Node.js not found! Install Node.js 20+ first."
    exit 1
fi
NODE_VERSION=$(node --version)
echo "   ✅ Found: $NODE_VERSION"

# Install frontend dependencies
echo ""
echo "📦 Installing frontend dependencies..."
cd apps/frontend
npm ci --prefer-offline
cd ../..

# Install pre-commit hooks
echo ""
echo "🔨 Installing pre-commit hooks..."
pre-commit install --hook-type pre-commit --hook-type commit-msg --hook-type pre-push

# Run pre-commit on all files (optional, for initial setup)
echo ""
echo "🧪 Testing hooks on existing files..."
echo "   (This may take a few minutes on first run)"
pre-commit run --all-files || true

# Summary
echo ""
echo "✅ Git Hooks installed successfully!"
echo ""
echo "📋 Configured Hooks:"
echo "   • commit-msg   → Validates Conventional Commits format"
echo "   • pre-commit   → Runs linters & formatters"
echo "   • pre-push     → Runs fast unit tests"
echo ""
echo "🚀 Next Steps:"
echo "   1. Make a commit: git commit -m 'feat: test hooks'"
echo "   2. Hooks will run automatically"
echo "   3. Fix any issues they report"
echo ""
echo "💡 To skip hooks (emergency only):"
echo "   git commit --no-verify -m '...'"
echo ""
echo "📚 Documentation:"
echo "   docs/CONVENTIONAL_COMMITS.md"
echo "   .pre-commit-config.yaml"
echo ""
