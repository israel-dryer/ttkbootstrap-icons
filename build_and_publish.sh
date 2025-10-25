#!/bin/bash

# Build and Publish Script for ttkbootstrap-icons
# Usage: ./build_and_publish.sh [test|prod]

set -e  # Exit on error

MODE=${1:-test}  # Default to test mode

echo "========================================="
echo "Building ttkbootstrap-icons"
echo "========================================="

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf dist/ build/ src/*.egg-info

# Build the package
echo "Building package..."
python -m build

# List the built files
echo ""
echo "Built files:"
ls -lh dist/

# Upload based on mode
if [ "$MODE" = "prod" ]; then
    echo ""
    echo "========================================="
    echo "Uploading to PyPI (PRODUCTION)"
    echo "========================================="
    read -p "Are you sure you want to upload to PyPI? (yes/no): " confirm
    if [ "$confirm" = "yes" ]; then
        python -m twine upload dist/*
        echo ""
        echo "✅ Successfully published to PyPI!"
        echo "Visit: https://pypi.org/project/ttkbootstrap-icons/"
    else
        echo "Upload cancelled."
    fi
else
    echo ""
    echo "========================================="
    echo "Uploading to TestPyPI"
    echo "========================================="
    python -m twine upload --repository testpypi dist/*
    echo ""
    echo "✅ Successfully published to TestPyPI!"
    echo "Test installation:"
    echo "  pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ ttkbootstrap-icons"
fi

echo ""
echo "Done!"
