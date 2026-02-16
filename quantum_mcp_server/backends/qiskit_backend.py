"""Qiskit backend adapter."""
import time
from typing import Dict, Any, List
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
from qiskit.qasm2 import dumps, loads

from .base import QuantumBackend, BackendType, CircuitResult, CircuitInfo


class QiskitBackend(QuantumBackend):
    """Adapter for IBM Qiskit simulator."""
    
    def __init__(self):
        super().__init__(BackendType.QISKIT)
        self.simulator = AerSimulator()
    
    def create_circuit(self, num_qubits: int, circuit_def: Dict[str, Any]) -> QuantumCircuit:
        """Create a Qiskit quantum circuit."""
        qc = QuantumCircuit(num_qubits)
        
        for gate_op in circuit_def.get('gates', []):
            gate_type = gate_op['type'].lower()
            qubits = gate_op.get('qubits', [])
            params = gate_op.get('params', [])
            
            # Single qubit gates
            if gate_type == 'h' or gate_type == 'hadamard':
                qc.h(qubits[0])
            elif gate_type == 'x' or gate_type == 'pauli_x':
                qc.x(qubits[0])
            elif gate_type == 'y' or gate_type == 'pauli_y':
                qc.y(qubits[0])
            elif gate_type == 'z' or gate_type == 'pauli_z':
                qc.z(qubits[0])
            elif gate_type == 's':
                qc.s(qubits[0])
            elif gate_type == 't':
                qc.t(qubits[0])
            elif gate_type == 'rx':
                qc.rx(params[0], qubits[0])
            elif gate_type == 'ry':
                qc.ry(params[0], qubits[0])
            elif gate_type == 'rz':
                qc.rz(params[0], qubits[0])
            
            # Two qubit gates
            elif gate_type in ['cx', 'cnot']:
                qc.cx(qubits[0], qubits[1])
            elif gate_type == 'cz':
                qc.cz(qubits[0], qubits[1])
            elif gate_type == 'swap':
                qc.swap(qubits[0], qubits[1])
            
            # Controlled-phase gate
            elif gate_type == 'cp':
                qc.cp(params[0], qubits[0], qubits[1])

            # Three qubit gates
            elif gate_type in ['ccx', 'toffoli']:
                qc.ccx(qubits[0], qubits[1], qubits[2])
        
        # Add measurements if specified
        if circuit_def.get('measure', True):
            qc.measure_all()
        
        return qc
    
    def execute_circuit(self, circuit: QuantumCircuit, shots: int = 1000, **kwargs) -> CircuitResult:
        """Execute a Qiskit circuit."""
        try:
            start_time = time.time()
            
            # Ensure circuit has measurements
            has_measurements = circuit.count_ops().get('measure', 0) > 0
            if not has_measurements:
                circuit = circuit.copy()
                circuit.measure_all()

            # Run simulation
            job = self.simulator.run(circuit, shots=shots, **kwargs)
            result = job.result()
            counts = result.get_counts()

            execution_time = time.time() - start_time

            # Convert counts to standard format with big-endian ordering
            # Qiskit uses little-endian (rightmost bit = qubit 0), so reverse
            formatted_counts = {str(k)[::-1]: int(v) for k, v in counts.items()}
            
            # Calculate probabilities
            total_shots = sum(formatted_counts.values())
            probabilities = {k: v/total_shots for k, v in formatted_counts.items()}
            
            return CircuitResult(
                backend=self.name,
                counts=formatted_counts,
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
    
    def get_circuit_info(self, circuit: QuantumCircuit) -> CircuitInfo:
        """Get Qiskit circuit information."""
        gate_types = []
        for instr in circuit.data:
            if hasattr(instr, 'operation'):
                gate_types.append(instr.operation.name)
            else:
                gate_types.append(str(instr[0]))
        
        return CircuitInfo(
            num_qubits=circuit.num_qubits,
            num_gates=len(circuit.data),
            depth=circuit.depth(),
            gate_types=list(set(gate_types)),
            backend=self.name
        )
    
    def from_qasm(self, qasm_str: str) -> QuantumCircuit:
        """Create circuit from QASM string."""
        return loads(qasm_str)
    
    def to_qasm(self, circuit: QuantumCircuit) -> str:
        """Convert circuit to QASM string."""
        return dumps(circuit)
