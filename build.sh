#!/usr/bin/env bash
#
# Build script for M8 Kit Creator
# Creates a standalone executable for the current platform
#
# Usage:
#   ./build.sh          # Build for current platform
#   ./build.sh clean    # Clean build artifacts

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Print colored message
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Clean build artifacts
clean() {
    print_info "Cleaning build artifacts..."
    rm -rf build dist __pycache__
    rm -rf m8_kitcreator/__pycache__
    find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
    print_info "Clean complete!"
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Build the application
build() {
    print_info "Starting M8 Kit Creator build..."
    echo

    # Check Python version
    print_info "Checking Python version..."
    PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    print_info "Python version: $PYTHON_VERSION"

    # Check if PyInstaller is installed
    if ! command_exists pyinstaller; then
        print_error "PyInstaller not found!"
        print_info "Installing build requirements..."
        pip3 install -r requirements-build.txt
    fi

    # Clean previous builds
    print_info "Cleaning previous builds..."
    rm -rf build dist

    # Detect platform
    if [[ "$OSTYPE" == "darwin"* ]]; then
        PLATFORM="macOS"
        OUTPUT_NAME="M8_KitCreator.app"
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        PLATFORM="Linux"
        OUTPUT_NAME="M8_KitCreator"
    else
        PLATFORM="Unknown"
        OUTPUT_NAME="M8_KitCreator"
    fi

    print_info "Building for $PLATFORM..."
    echo

    # Run PyInstaller
    print_info "Running PyInstaller..."
    pyinstaller --clean M8_KitCreator.spec

    # Check if build succeeded
    if [[ "$OSTYPE" == "darwin"* ]]; then
        if [ -d "dist/M8_KitCreator.app" ]; then
            print_info "Build successful!"
            print_info "Application: dist/M8_KitCreator.app"
            echo
            print_info "To run:"
            echo "  open dist/M8_KitCreator.app"
            echo
            print_info "To create DMG (requires create-dmg):"
            echo "  create-dmg --volname 'M8 Kit Creator' \\"
            echo "    --window-pos 200 120 --window-size 800 400 \\"
            echo "    --icon-size 100 --app-drop-link 600 185 \\"
            echo "    dist/M8_KitCreator.dmg dist/M8_KitCreator.app"
        else
            print_error "Build failed! Application not found."
            exit 1
        fi
    else
        if [ -f "dist/M8_KitCreator" ]; then
            print_info "Build successful!"
            print_info "Executable: dist/M8_KitCreator"
            echo
            # Make executable
            chmod +x dist/M8_KitCreator
            print_info "To run:"
            echo "  ./dist/M8_KitCreator"
            echo
            print_info "To create portable archive:"
            echo "  cd dist && tar -czf M8_KitCreator-linux-$(uname -m).tar.gz M8_KitCreator"
        else
            print_error "Build failed! Executable not found."
            exit 1
        fi
    fi

    echo
    print_info "Build artifacts in: dist/"
    du -sh dist/* 2>/dev/null || true
}

# Main script
case "${1:-build}" in
    clean)
        clean
        ;;
    build)
        build
        ;;
    rebuild)
        clean
        build
        ;;
    *)
        echo "Usage: $0 {build|clean|rebuild}"
        echo
        echo "Commands:"
        echo "  build    - Build the application (default)"
        echo "  clean    - Clean build artifacts"
        echo "  rebuild  - Clean and build"
        exit 1
        ;;
esac
