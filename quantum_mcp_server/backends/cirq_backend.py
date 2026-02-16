"""Cirq backend adapter."""
import time
from typing import Dict, Any, List
import cirq

from .base import QuantumBackend, BackendType, CircuitResult, CircuitInfo


class CirqBackend(QuantumBackend):
    """Adapter for Google Cirq simulator."""
    
    def __init__(self):
        super().__init__(BackendType.CIRQ)
        self.simulator = cirq.Simulator()
    
    def create_circuit(self, num_qubits: int, circuit_def: Dict[str, Any]) -> cirq.Circuit:
        """Create a Cirq quantum circuit."""
        qubits = cirq.LineQubit.range(num_qubits)
        circuit = cirq.Circuit()
        
        for gate_op in circuit_def.get('gates', []):
            gate_type = gate_op['type'].lower()
            qubit_indices = gate_op.get('qubits', [])
            params = gate_op.get('params', [])
            
            # Single qubit gates
            if gate_type == 'h' or gate_type == 'hadamard':
                circuit.append(cirq.H(qubits[qubit_indices[0]]))
            elif gate_type == 'x' or gate_type == 'pauli_x':
                circuit.append(cirq.X(qubits[qubit_indices[0]]))
            elif gate_type == 'y' or gate_type == 'pauli_y':
                circuit.append(cirq.Y(qubits[qubit_indices[0]]))
            elif gate_type == 'z' or gate_type == 'pauli_z':
                circuit.append(cirq.Z(qubits[qubit_indices[0]]))
            elif gate_type == 's':
                circuit.append(cirq.S(qubits[qubit_indices[0]]))
            elif gate_type == 't':
                circuit.append(cirq.T(qubits[qubit_indices[0]]))
            elif gate_type == 'rx':
                circuit.append(cirq.rx(params[0])(qubits[qubit_indices[0]]))
            elif gate_type == 'ry':
                circuit.append(cirq.ry(params[0])(qubits[qubit_indices[0]]))
            elif gate_type == 'rz':
                circuit.append(cirq.rz(params[0])(qubits[qubit_indices[0]]))
            
            # Two qubit gates
            elif gate_type in ['cx', 'cnot']:
                circuit.append(cirq.CNOT(qubits[qubit_indices[0]], qubits[qubit_indices[1]]))
            elif gate_type == 'cz':
                circuit.append(cirq.CZ(qubits[qubit_indices[0]], qubits[qubit_indices[1]]))
            elif gate_type == 'swap':
                circuit.append(cirq.SWAP(qubits[qubit_indices[0]], qubits[qubit_indices[1]]))
            
            # Three qubit gates
            elif gate_type in ['ccx', 'toffoli']:
                circuit.append(cirq.TOFFOLI(qubits[qubit_indices[0]], qubits[qubit_indices[1]], qubits[qubit_indices[2]]))
        
        # Add measurements
        if circuit_def.get('measure', True):
            circuit.append(cirq.measure(*qubits, key='result'))
        
        return circuit
    
    def execute_circuit(self, circuit: cirq.Circuit, shots: int = 1000, **kwargs) -> CircuitResult:
        """Execute a Cirq circuit."""
        try:
            start_time = time.time()
            
            # Run simulation
            result = self.simulator.run(circuit, repetitions=shots)
            
            execution_time = time.time() - start_time
            
            # Get measurements
            measurements = result.measurements['result']
            
            # Convert to counts
            counts = {}
            for measurement in measurements:
                bitstring = ''.join(str(int(b)) for b in measurement)
                counts[bitstring] = counts.get(bitstring, 0) + 1
            
            # Calculate probabilities
            total = sum(counts.values())
            probabilities = {k: v/total for k, v in counts.items()}
            
            return CircuitResult(
                backend=self.name,
                counts=counts,
                probabilities=probabilities,
                execution_time=execution_time,
                metadata={'shots': shots, 'success': True},
                raw_result=result
            )
        
        except Exception as e:
            return CircuitResult(
                backend=self.name,
                error=str(e),
                metadata={'shots': shots, 'success': False}
            )
    
    def get_circuit_info(self, circuit: cirq.Circuit) -> CircuitInfo:
        """Get Cirq circuit information."""
        gate_types = []
        for moment in circuit:
            for op in moment:
                gate_types.append(str(op.gate))
        
        return CircuitInfo(
            num_qubits=len(circuit.all_qubits()),
            num_gates=len(list(circuit.all_operations())),
            depth=len(circuit),
            gate_types=list(set(gate_types)),
            backend=self.name
        )
    
    def from_qasm(self, qasm_str: str) -> cirq.Circuit:
        """Create circuit from QASM string."""
        return cirq.Circuit(cirq.qasm(qasm_str))
    
    def to_qasm(self, circuit: cirq.Circuit) -> str:
        """Convert circuit to QASM string."""
        return str(circuit.to_qasm())
