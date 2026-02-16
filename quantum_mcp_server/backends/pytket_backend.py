"""PyTKET backend adapter."""
import time
from typing import Dict, Any, List
from pytket import Circuit
from pytket.extensions.qiskit import AerBackend

from .base import QuantumBackend, BackendType, CircuitResult, CircuitInfo


class PyTKETBackend(QuantumBackend):
    """Adapter for Quantinuum PyTKET."""
    
    def __init__(self):
        super().__init__(BackendType.PYTKET)
        self.backend = AerBackend()
    
    def create_circuit(self, num_qubits: int, circuit_def: Dict[str, Any]) -> Circuit:
        """Create a PyTKET quantum circuit."""
        circuit = Circuit(num_qubits)
        
        for gate_op in circuit_def.get('gates', []):
            gate_type = gate_op['type'].lower()
            qubits = gate_op.get('qubits', [])
            params = gate_op.get('params', [])
            
            # Single qubit gates
            if gate_type == 'h' or gate_type == 'hadamard':
                circuit.H(qubits[0])
            elif gate_type == 'x' or gate_type == 'pauli_x':
                circuit.X(qubits[0])
            elif gate_type == 'y' or gate_type == 'pauli_y':
                circuit.Y(qubits[0])
            elif gate_type == 'z' or gate_type == 'pauli_z':
                circuit.Z(qubits[0])
            elif gate_type == 's':
                circuit.S(qubits[0])
            elif gate_type == 't':
                circuit.T(qubits[0])
            elif gate_type == 'rx':
                circuit.Rx(params[0], qubits[0])
            elif gate_type == 'ry':
                circuit.Ry(params[0], qubits[0])
            elif gate_type == 'rz':
                circuit.Rz(params[0], qubits[0])
            
            # Two qubit gates
            elif gate_type in ['cx', 'cnot']:
                circuit.CX(qubits[0], qubits[1])
            elif gate_type == 'cz':
                circuit.CZ(qubits[0], qubits[1])
            elif gate_type == 'swap':
                circuit.SWAP(qubits[0], qubits[1])
            
            # Three qubit gates
            elif gate_type in ['ccx', 'toffoli']:
                circuit.CCX(qubits[0], qubits[1], qubits[2])
        
        # Add measurements
        if circuit_def.get('measure', True):
            circuit.measure_all()
        
        return circuit
    
    def execute_circuit(self, circuit: Circuit, shots: int = 1000, **kwargs) -> CircuitResult:
        """Execute a PyTKET circuit."""
        try:
            start_time = time.time()
            
            # Compile circuit
            compiled_circuit = self.backend.get_compiled_circuit(circuit)
            
            # Execute
            handle = self.backend.process_circuit(compiled_circuit, n_shots=shots)
            result = self.backend.get_result(handle)
            
            execution_time = time.time() - start_time
            
            # Get counts
            counts_dict = result.get_counts()
            
            # Convert to standard format
            counts = {}
            for outcome, count in counts_dict.items():
                # outcome is a tuple like (0, 1) or (1, 1)
                bitstring = ''.join(str(b) for b in outcome)
                counts[bitstring] = count
            
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
    
    def get_circuit_info(self, circuit: Circuit) -> CircuitInfo:
        """Get PyTKET circuit information."""
        return CircuitInfo(
            num_qubits=circuit.n_qubits,
            num_gates=circuit.n_gates,
            depth=circuit.depth(),
            gate_types=[],  # PyTKET doesn't easily expose this
            backend=self.name
        )
    
    def from_qasm(self, qasm_str: str) -> Circuit:
        """Create circuit from QASM string."""
        return Circuit.from_qasm_str(qasm_str)
    
    def to_qasm(self, circuit: Circuit) -> str:
        """Convert circuit to QASM string."""
        return circuit.to_qasm_str()
