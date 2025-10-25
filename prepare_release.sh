#!/bin/bash

# Prepare Release Script
# This script prepares your repository for a clean v1.0.0 release

set -e

VERSION=${1:-v1.0.0}

echo "========================================="
echo "Preparing Release: $VERSION"
echo "========================================="

# Clean build artifacts
echo "Cleaning build artifacts..."
rm -rf dist/ build/ src/*.egg-info __pycache__ src/**/__pycache__

# Check git status
echo ""
echo "Current git status:"
git status --short

# Stage all changes
echo ""
echo "Staging all changes..."
git add .

# Show what will be committed
echo ""
echo "Changes to be committed:"
git status --short

# Prompt for commit message
echo ""
read -p "Enter commit message (default: 'Prepare release $VERSION'): " commit_msg
commit_msg=${commit_msg:-"Prepare release $VERSION"}

# Commit
echo ""
echo "Committing changes..."
git commit -m "$commit_msg" || echo "Nothing to commit or commit failed"

# Create tag
echo ""
read -p "Create tag $VERSION? (yes/no): " confirm_tag
if [ "$confirm_tag" = "yes" ]; then
    git tag -a $VERSION -m "Release $VERSION"
    echo "✅ Tag $VERSION created"

    # Show version that will be built
    echo ""
    echo "Version that will be built:"
    python -m setuptools_scm

    # Prompt to push
    echo ""
    read -p "Push to remote? (yes/no): " confirm_push
    if [ "$confirm_push" = "yes" ]; then
        git push origin main
        git push origin $VERSION
        echo "✅ Pushed to remote"
    fi
else
    echo "Tag creation skipped"
fi

echo ""
echo "========================================="
echo "Release preparation complete!"
echo "========================================="
echo ""
echo "Next steps:"
echo "1. Run: ./build_and_publish.sh test   # Test on TestPyPI"
echo "2. Run: ./build_and_publish.sh prod   # Publish to PyPI"
