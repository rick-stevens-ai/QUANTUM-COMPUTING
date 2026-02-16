#!/bin/bash
# Launcher script for Quantum MCP Server

cd "$(dirname "$0")"

echo "╔════════════════════════════════════════════════════════╗"
echo "║    Quantum Computing MCP Server                        ║"
echo "║    NVIDIA DGX SPARK GB10                               ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

# Check Python and dependencies
python3 server.py
