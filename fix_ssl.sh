#!/bin/bash

# SSL Certificate Fix Script for macOS

echo "=================================="
echo "Fixing SSL Certificate Issues..."
echo "=================================="

# Method 1: Install Python certificates (recommended)
echo ""
echo "Method 1: Installing Python certificates..."

# Find Python installation path
PYTHON_PATH=$(which python3)
PYTHON_VERSION=$(python3 --version | awk '{print $2}' | cut -d. -f1,2)

# Try to run the Install Certificates command
CERT_COMMAND="/Applications/Python ${PYTHON_VERSION}/Install Certificates.command"
if [ -f "$CERT_COMMAND" ]; then
    echo "Found certificate installer, running it..."
    "$CERT_COMMAND"
    echo "✓ Certificates installed!"
else
    echo "Certificate installer not found at standard location."
    echo "Trying alternative method..."
fi

# Method 2: Update certifi package
echo ""
echo "Method 2: Updating certifi package..."
pip install --upgrade certifi

# Method 3: Install certificates via pip
echo ""
echo "Method 3: Installing certificates..."
python3 << 'PYEND'
import ssl
import certifi

print(f"✓ Certifi location: {certifi.where()}")
print(f"✓ SSL version: {ssl.OPENSSL_VERSION}")
PYEND

echo ""
echo "=================================="
echo "SSL fix complete!"
echo "=================================="
echo ""
echo "If the issue persists, you can temporarily disable SSL verification"
echo "by setting an environment variable (NOT recommended for production):"
echo ""
echo "  export PYTHONHTTPSVERIFY=0"
echo ""

