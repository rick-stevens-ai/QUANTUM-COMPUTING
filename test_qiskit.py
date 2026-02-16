#!/usr/bin/env python3
"""Test IBM Qiskit installation"""
import qiskit
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator

print("Testing Qiskit...")
# Create a simple quantum circuit
qc = QuantumCircuit(2, 2)
qc.h(0)  # Hadamard gate on qubit 0
qc.cx(0, 1)  # CNOT gate
qc.measure([0, 1], [0, 1])

# Simulate
simulator = AerSimulator()
job = simulator.run(qc, shots=1000)
result = job.result()
counts = result.get_counts()

print(f"✓ Qiskit {qiskit.__version__} working!")
print(f"  Bell state measurement results: {counts}")
