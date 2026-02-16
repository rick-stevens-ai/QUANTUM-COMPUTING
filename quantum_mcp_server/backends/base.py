"""Base backend adapter interface for quantum simulators."""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum


class BackendType(Enum):
    """Supported quantum backend types."""
    QISKIT = "qiskit"
    PENNYLANE = "pennylane"
    CIRQ = "cirq"
    PYTKET = "pytket"
    CLASSIQ = "classiq"


@dataclass
class CircuitResult:
    """Standardized quantum circuit execution result."""
    backend: str
    counts: Optional[Dict[str, int]] = None
    statevector: Optional[List[complex]] = None
    expectation_values: Optional[Dict[str, float]] = None
    probabilities: Optional[Dict[str, float]] = None
    execution_time: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None
    raw_result: Optional[Any] = None
    error: Optional[str] = None


@dataclass
class CircuitInfo:
    """Information about a quantum circuit."""
    num_qubits: int
    num_gates: int
    depth: int
    gate_types: List[str]
    backend: str


class QuantumBackend(ABC):
    """Abstract base class for quantum backend adapters."""
    
    def __init__(self, backend_type: BackendType):
        self.backend_type = backend_type
        self.name = backend_type.value
    
    @abstractmethod
    def create_circuit(self, num_qubits: int, circuit_def: Dict[str, Any]) -> Any:
        """
        Create a quantum circuit from definition.
        
        Args:
            num_qubits: Number of qubits
            circuit_def: Circuit definition with gates
            
        Returns:
            Backend-specific circuit object
        """
        pass
    
    @abstractmethod
    def execute_circuit(self, circuit: Any, shots: int = 1000, **kwargs) -> CircuitResult:
        """
        Execute a quantum circuit.
        
        Args:
            circuit: Backend-specific circuit
            shots: Number of measurement shots
            **kwargs: Backend-specific options
            
        Returns:
            CircuitResult with standardized output
        """
        pass
    
    @abstractmethod
    def get_circuit_info(self, circuit: Any) -> CircuitInfo:
        """Get information about a circuit."""
        pass
    
    @abstractmethod
    def from_qasm(self, qasm_str: str) -> Any:
        """Create circuit from QASM string."""
        pass
    
    @abstractmethod
    def to_qasm(self, circuit: Any) -> str:
        """Convert circuit to QASM string."""
        pass
    
    def validate_circuit_def(self, circuit_def: Dict[str, Any]) -> bool:
        """Validate circuit definition format."""
        required_keys = ['gates']
        return all(key in circuit_def for key in required_keys)
