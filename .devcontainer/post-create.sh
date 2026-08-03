#!/bin/bash
set -e

echo "Upgrading Azure CLI to latest version..."
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

echo "Installing Marp CLI (optional; used only for slide decks) ..."
npm install -g @marp-team/marp-cli || echo "  ! Marp CLI install failed — continuing (only needed for slide authoring)."

echo "Installing uv ..."
curl -LsSf https://astral.sh/uv/install.sh | sh

echo "Installing Python dependencies ..."
pip install --upgrade pip
pip install -r requirements-dev.txt --quiet

echo "Post-create setup complete."