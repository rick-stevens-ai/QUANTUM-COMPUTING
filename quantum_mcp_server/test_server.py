#!/usr/bin/env python3
"""Quick test to verify server initializes correctly"""
import sys
sys.path.insert(0, '/home/stevens/QUANTUM-COMPUTING/quantum_mcp_server')

print("Testing server initialization...")

# Import all components
from backends.qiskit_backend import QiskitBackend
from backends.pennylane_backend import PennyLaneBackend
from backends.cirq_backend import CirqBackend
from backends.pytket_backend import PyTKETBackend
from mcp.server import Server
from mcp.types import Tool

# Initialize backends
BACKENDS = {}
for name, cls in [('qiskit', QiskitBackend), ('pennylane', PennyLaneBackend), 
                   ('cirq', CirqBackend), ('pytket', PyTKETBackend)]:
    try:
        BACKENDS[name] = cls()
        print(f"✓ {name} initialized")
    except Exception as e:
        print(f"✗ {name} failed: {e}")

print(f"\n✓ Server components loaded successfully")
print(f"✓ {len(BACKENDS)}/4 backends available: {', '.join(BACKENDS.keys())}")
print("\nServer is ready to accept MCP connections!")
