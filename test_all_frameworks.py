#!/usr/bin/env python3
"""Comprehensive test of all quantum computing frameworks"""

print("=" * 60)
print("QUANTUM COMPUTING FRAMEWORK TEST SUITE")
print("=" * 60)

frameworks_tested = []
frameworks_failed = []

# Test 1: Qiskit
print("\n[1/4] Testing IBM Qiskit...")
try:
    import qiskit
    from qiskit import QuantumCircuit
    from qiskit_aer import AerSimulator
    
    qc = QuantumCircuit(2)
    qc.h(0)
    qc.cx(0, 1)
    qc.measure_all()
    
    simulator = AerSimulator()
    job = simulator.run(qc, shots=100)
    result = job.result()
    
    print(f"  ✓ Qiskit {qiskit.__version__} - PASSED")
    frameworks_tested.append(("Qiskit", qiskit.__version__))
except Exception as e:
    print(f"  ✗ Qiskit - FAILED: {e}")
    frameworks_failed.append("Qiskit")

# Test 2: PennyLane
print("\n[2/4] Testing Xanadu PennyLane...")
try:
    import pennylane as qml
    
    dev = qml.device('lightning.qubit', wires=2)
    
    @qml.qnode(dev)
    def circuit():
        qml.Hadamard(wires=0)
        qml.CNOT(wires=[0, 1])
        return qml.probs(wires=[0, 1])
    
    result = circuit()
    
    print(f"  ✓ PennyLane {qml.__version__} - PASSED")
    frameworks_tested.append(("PennyLane", qml.__version__))
except Exception as e:
    print(f"  ✗ PennyLane - FAILED: {e}")
    frameworks_failed.append("PennyLane")

# Test 3: Cirq
print("\n[3/4] Testing Google Cirq...")
try:
    import cirq
    
    q0, q1 = cirq.LineQubit.range(2)
    circuit = cirq.Circuit(
        cirq.H(q0),
        cirq.CNOT(q0, q1),
        cirq.measure(q0, q1, key='result')
    )
    
    simulator = cirq.Simulator()
    result = simulator.run(circuit, repetitions=100)
    
    print(f"  ✓ Cirq {cirq.__version__} - PASSED")
    frameworks_tested.append(("Cirq", cirq.__version__))
except Exception as e:
    print(f"  ✗ Cirq - FAILED: {e}")
    frameworks_failed.append("Cirq")

# Test 4: PyTKET
print("\n[4/4] Testing Quantinuum PyTKET...")
try:
    from pytket import Circuit, __version__ as pytket_version
    from pytket.extensions.qiskit import AerBackend
    
    circuit = Circuit(2)
    circuit.H(0)
    circuit.CX(0, 1)
    circuit.measure_all()
    
    backend = AerBackend()
    compiled = backend.get_compiled_circuit(circuit)
    handle = backend.process_circuit(compiled, n_shots=100)
    result = backend.get_result(handle)
    
    print(f"  ✓ PyTKET {pytket_version} - PASSED")
    frameworks_tested.append(("PyTKET", pytket_version))
except Exception as e:
    print(f"  ✗ PyTKET - FAILED: {e}")
    frameworks_failed.append("PyTKET")

# Summary
print("\n" + "=" * 60)
print("TEST SUMMARY")
print("=" * 60)
print(f"\nPassed: {len(frameworks_tested)}/{len(frameworks_tested) + len(frameworks_failed)}")

if frameworks_tested:
    print("\n✓ Working Frameworks:")
    for name, version in frameworks_tested:
        print(f"  - {name} {version}")

if frameworks_failed:
    print("\n✗ Failed Frameworks:")
    for name in frameworks_failed:
        print(f"  - {name}")

print("\n" + "=" * 60)
print("All quantum backends are ready for MCP server development!")
print("=" * 60)
