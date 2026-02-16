#!/bin/bash
# MCP Server launcher script using official MCP SDK

# Use conda's Python explicitly
export PATH="/home/stevens/miniconda3/bin:$PATH"
cd /home/stevens/QUANTUM-COMPUTING/quantum_mcp_server
export PYTHONPATH=/home/stevens/QUANTUM-COMPUTING/quantum_mcp_server

# Use the official MCP SDK server
exec /home/stevens/miniconda3/bin/python3 server_mcp.py
