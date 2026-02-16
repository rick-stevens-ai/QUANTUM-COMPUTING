#!/usr/bin/env python3
"""Test Classiq installation"""
from classiq import *

print("Testing Classiq...")

# Create a simple Bell state circuit
@qfunc
def main(res: Output[QArray[QBit]]):
    allocate(2, res)
    H(res[0])
    CX(res[0], res[1])

# Create and synthesize the model
print("  Creating quantum model...")
model = create_model(main)

print("  Synthesizing quantum circuit...")
qprog = synthesize(model)

print(f"✓ Classiq 1.1.0 working!")
print(f"  Bell state circuit created successfully")
print(f"  Width (qubits): {qprog.data.width}")
print(f"  Gate count: {qprog.data.gate_count}")
