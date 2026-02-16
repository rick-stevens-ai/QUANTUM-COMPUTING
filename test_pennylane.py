#!/usr/bin/env python3
"""Test PennyLane installation"""
import pennylane as qml
import numpy as np

print("Testing PennyLane...")
# Create a simple quantum device
dev = qml.device('lightning.qubit', wires=2)

@qml.qnode(dev)
def circuit():
    qml.Hadamard(wires=0)
    qml.CNOT(wires=[0, 1])
    return qml.expval(qml.PauliZ(0) @ qml.PauliZ(1))

result = circuit()
print(f"✓ PennyLane {qml.__version__} working!")
print(f"  Bell state expectation value: {result}")
