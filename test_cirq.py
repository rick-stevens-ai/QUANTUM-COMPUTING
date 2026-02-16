#!/usr/bin/env python3
"""Test Google Cirq installation"""
import cirq

print("Testing Cirq...")
# Create a simple quantum circuit
q0, q1 = cirq.LineQubit.range(2)
circuit = cirq.Circuit(
    cirq.H(q0),
    cirq.CNOT(q0, q1),
    cirq.measure(q0, q1, key='result')
)

# Simulate
simulator = cirq.Simulator()
result = simulator.run(circuit, repetitions=1000)
counts = result.histogram(key='result')

print(f"✓ Cirq {cirq.__version__} working!")
print(f"  Bell state measurement results: {dict(counts)}")
