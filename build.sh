#!/usr/bin/env bash
# Render build script
set -e

echo "==> Installing Python dependencies..."
pip install -r requirements.txt

echo "==> Downloading spaCy model..."
python -m spacy download en_core_web_sm || echo "spaCy model download failed - NLP features will be disabled"

echo "==> Creating required directories..."
mkdir -p /tmp/uploads /tmp/reports

echo "==> Build complete!"
