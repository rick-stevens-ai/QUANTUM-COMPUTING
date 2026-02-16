#!/usr/bin/env python3
"""
Quantum Computing MCP Server - 4 Backends (Qiskit, PennyLane, Cirq, PyTKET)
"""
import json
import asyncio
from typing import Any
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# Import backends
import sys
sys.path.insert(0, '/home/stevens/QUANTUM-COMPUTING/quantum_mcp_server')
from backends.qiskit_backend import QiskitBackend
from backends.pennylane_backend import PennyLaneBackend
from backends.cirq_backend import CirqBackend
from backends.pytket_backend import PyTKETBackend

# Initialize backends
BACKENDS = {}
for name, cls in [('qiskit', QiskitBackend), ('pennylane', PennyLaneBackend), 
                   ('cirq', CirqBackend), ('pytket', PyTKETBackend)]:
    try:
        BACKENDS[name] = cls()
    except Exception as e:
        print(f"Failed to initialize {name}: {e}")

AVAILABLE = {k: v is not None for k, v in BACKENDS.items()}

app = Server("quantum-simulator")

@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(name="list_backends", description="List quantum backends", 
             inputSchema={"type": "object", "properties": {}, "required": []}),
        Tool(name="create_bell_state", description="Create Bell state",
             inputSchema={"type": "object", "properties": {
                 "backend": {"type": "string", "default": "qiskit"},
                 "shots": {"type": "number", "default": 1000}}, "required": []}),
        Tool(name="execute_circuit", description="Execute quantum circuit",
             inputSchema={"type": "object", "properties": {
                 "num_qubits": {"type": "number"},
                 "gates": {"type": "array", "items": {"type": "object"}},
                 "backend": {"type": "string", "default": "qiskit"},
                 "shots": {"type": "number", "default": 1000}},
                 "required": ["num_qubits", "gates"]}),
        Tool(name="create_ghz_state", description="Create GHZ state",
             inputSchema={"type": "object", "properties": {
                 "num_qubits": {"type": "number"},
                 "backend": {"type": "string", "default": "qiskit"},
                 "shots": {"type": "number", "default": 1000}},
                 "required": ["num_qubits"]})
    ]

@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    if name == "list_backends":
        result = {"backends": {
            "qiskit": {"available": AVAILABLE.get('qiskit', False), 
                      "description": "IBM Qiskit Aer", "version": "2.3.0"},
            "pennylane": {"available": AVAILABLE.get('pennylane', False),
                         "description": "Xanadu PennyLane", "version": "0.44.0"},
            "cirq": {"available": AVAILABLE.get('cirq', False),
                    "description": "Google Cirq", "version": "1.6.1"},
            "pytket": {"available": AVAILABLE.get('pytket', False),
                      "description": "Quantinuum TKET", "version": "2.13.0"}
        }}
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    
    backend_name = arguments.get("backend", "qiskit")
    if backend_name not in BACKENDS or BACKENDS[backend_name] is None:
        return [TextContent(type="text", text=json.dumps({"error": f"Backend {backend_name} not available"}))]
    
    backend = BACKENDS[backend_name]
    shots = int(arguments.get("shots", 1000))
    
    if name == "create_bell_state":
        gates = [{"type": "h", "qubits": [0]}, {"type": "cx", "qubits": [0, 1]}]
        circuit = backend.create_circuit(2, {"gates": gates, "measure": True})
        result = backend.execute_circuit(circuit, shots=shots)
    elif name == "create_ghz_state":
        num_qubits = int(arguments["num_qubits"])
        if num_qubits < 2:
            return [TextContent(type="text", text=json.dumps({"error": "GHZ needs >= 2 qubits"}))]
        gates = [{"type": "h", "qubits": [0]}]
        for i in range(1, num_qubits):
            gates.append({"type": "cx", "qubits": [0, i]})
        circuit = backend.create_circuit(num_qubits, {"gates": gates, "measure": True})
        result = backend.execute_circuit(circuit, shots=shots)
    elif name == "execute_circuit":
        num_qubits = int(arguments["num_qubits"])
        gates = arguments["gates"]
        circuit = backend.create_circuit(num_qubits, {"gates": gates, "measure": True})
        result = backend.execute_circuit(circuit, shots=shots)
    else:
        return [TextContent(type="text", text=json.dumps({"error": f"Unknown tool: {name}"}))]
    
    if result.error:
        return [TextContent(type="text", text=json.dumps({"error": result.error, "backend": backend_name}))]
    
    response = {"success": True, "backend": backend_name, "counts": result.counts,
                "probabilities": result.probabilities, "execution_time": result.execution_time}
    return [TextContent(type="text", text=json.dumps(response, indent=2))]

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())
