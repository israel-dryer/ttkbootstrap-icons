#!/bin/bash
# Deploy MkDocs documentation to GitHub Pages
# Usage: ./deploy-docs.sh

set -e

echo -e "\033[36mDeploying MkDocs documentation to GitHub Pages...\033[0m"

# Check if mkdocs is installed
if ! command -v mkdocs &> /dev/null; then
    echo -e "\033[31mError: mkdocs is not installed or not in PATH\033[0m"
    echo -e "\033[33mInstall with: pip install mkdocs mkdocs-material mkdocs-gen-files\033[0m"
    exit 1
fi

echo -e "\033[32mUsing $(mkdocs --version)\033[0m"

# Deploy documentation
echo -e "\n\033[33mDeploying documentation...\033[0m"
mkdocs gh-deploy --force

echo -e "\n\033[32m✓ Documentation deployed successfully!\033[0m"
echo -e "\033[36mView your documentation at the GitHub Pages URL for this repository.\033[0m"