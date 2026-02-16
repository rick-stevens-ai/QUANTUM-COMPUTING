#!/usr/bin/env python3
"""Test Quantinuum TKET installation"""
from pytket import Circuit
from pytket.extensions.qiskit import AerBackend

print("Testing PyTKET...")
# Create a simple quantum circuit
circuit = Circuit(2, 2)
circuit.H(0)
circuit.CX(0, 1)
circuit.measure_all()

# Simulate using Aer backend
backend = AerBackend()
compiled_circuit = backend.get_compiled_circuit(circuit)
handle = backend.process_circuit(compiled_circuit, n_shots=1000)
result = backend.get_result(handle)
counts = result.get_counts()

print(f"✓ PyTKET working!")
print(f"  Bell state measurement results: {dict(counts)}")
