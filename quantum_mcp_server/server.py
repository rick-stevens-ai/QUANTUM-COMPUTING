"""
Quantum Computing MCP Server
A unified FastMCP server interface for multiple quantum computing frameworks.
"""
import json
import subprocess
import time
from typing import Dict, Any, List, Optional
from fastmcp import FastMCP

# Import backends
from backends.qiskit_backend import QiskitBackend

# Initialize FastMCP server
mcp = FastMCP("Quantum Computing Simulator")

# Global backend registry
BACKENDS = {
    'qiskit': QiskitBackend(),
}

# Backend availability cache
BACKEND_STATUS = {}


def check_backend_availability() -> Dict[str, bool]:
    """Check which backends are available."""
    global BACKEND_STATUS
    
    status = {}
    
    # Qiskit
    try:
        from qiskit import QuantumCircuit
        status['qiskit'] = True
    except:
        status['qiskit'] = False
    
    # PennyLane
    try:
        import pennylane as qml
        status['pennylane'] = True
    except:
        status['pennylane'] = False
    
    # Cirq
    try:
        import cirq
        status['cirq'] = True
    except:
        status['cirq'] = False
    
    # PyTKET
    try:
        from pytket import Circuit
        status['pytket'] = True
    except:
        status['pytket'] = False
    
    # Classiq (check conda env)
    try:
        result = subprocess.run(
            ['conda', 'run', '-n', 'classiq-env', 'python', '-c', 'import classiq'],
            capture_output=True,
            timeout=5
        )
        status['classiq'] = (result.returncode == 0)
    except:
        status['classiq'] = False
    
    BACKEND_STATUS = status
    return status


@mcp.tool()
def list_backends() -> dict:
    """
    List all available quantum computing backends and their status.
    
    Returns:
        Dictionary with backend names and availability status.
    """
    status = check_backend_availability()
    
    backend_info = {
        'qiskit': {
            'available': status.get('qiskit', False),
            'description': 'IBM Qiskit with Aer Simulator',
            'version': '2.3.0',
            'python_env': '3.13'
        },
        'pennylane': {
            'available': status.get('pennylane', False),
            'description': 'Xanadu PennyLane with Lightning',
            'version': '0.44.0',
            'python_env': '3.13'
        },
        'cirq': {
            'available': status.get('cirq', False),
            'description': 'Google Cirq Simulator',
            'version': '1.6.1',
            'python_env': '3.13'
        },
        'pytket': {
            'available': status.get('pytket', False),
            'description': 'Quantinuum TKET',
            'version': '2.13.0',
            'python_env': '3.13'
        },
        'classiq': {
            'available': status.get('classiq', False),
            'description': 'Classiq Platform',
            'version': '1.1.0',
            'python_env': '3.12 (conda: classiq-env)'
        }
    }
    
    return {
        'total_backends': len(backend_info),
        'available_backends': sum(1 for b in backend_info.values() if b['available']),
        'backends': backend_info
    }


@mcp.tool()
def create_circuit(
    num_qubits: int,
    gates: list,
    backend: str = 'qiskit',
    measure: bool = True
) -> dict:
    """
    Create a quantum circuit using standardized gate definitions.
    
    Args:
        num_qubits: Number of qubits in the circuit
        gates: List of gate operations. Each gate is a dict with:
               - type: Gate type (h, x, y, z, rx, ry, rz, cx, cnot, cz, swap, ccx)
               - qubits: List of qubit indices the gate acts on
               - params: Optional list of parameters (for parametric gates)
        backend: Backend to use ('qiskit', 'pennylane', 'cirq', 'pytket', 'classiq')
        measure: Whether to add measurements at the end
    
    Returns:
        Dictionary with circuit information and QASM representation
    
    Example gates:
        [
            {"type": "h", "qubits": [0]},
            {"type": "cx", "qubits": [0, 1]},
            {"type": "rx", "qubits": [0], "params": [1.57]}
        ]
    """
    if backend not in BACKENDS:
        return {'error': f'Backend {backend} not supported or not loaded'}
    
    backend_obj = BACKENDS[backend]
    
    circuit_def = {
        'gates': gates,
        'measure': measure
    }
    
    try:
        circuit = backend_obj.create_circuit(num_qubits, circuit_def)
        info = backend_obj.get_circuit_info(circuit)
        qasm = backend_obj.to_qasm(circuit)
        
        return {
            'success': True,
            'backend': backend,
            'circuit_info': {
                'num_qubits': info.num_qubits,
                'num_gates': info.num_gates,
                'depth': info.depth,
                'gate_types': info.gate_types
            },
            'qasm': qasm,
            'circuit_id': f'{backend}_{int(time.time())}'
        }
    
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'backend': backend
        }


@mcp.tool()
def execute_circuit(
    num_qubits: int,
    gates: list,
    backend: str = 'qiskit',
    shots: int = 1000,
    qasm: str | None = None
) -> dict:
    """
    Execute a quantum circuit on a specified backend.
    
    Args:
        num_qubits: Number of qubits (required if not using qasm)
        gates: Gate definitions (required if not using qasm)
        backend: Backend to execute on
        shots: Number of measurement shots
        qasm: Optional QASM string representation of circuit
    
    Returns:
        Execution results with counts, probabilities, and timing
    """
    if backend not in BACKENDS:
        return {'error': f'Backend {backend} not supported'}
    
    backend_obj = BACKENDS[backend]
    
    try:
        # Create circuit from QASM or gate definitions
        if qasm:
            circuit = backend_obj.from_qasm(qasm)
        elif gates and num_qubits:
            circuit = backend_obj.create_circuit(num_qubits, {'gates': gates, 'measure': True})
        else:
            return {'error': 'Must provide either qasm or (num_qubits + gates)'}
        
        # Execute
        result = backend_obj.execute_circuit(circuit, shots=shots)
        
        if result.error:
            return {
                'success': False,
                'error': result.error,
                'backend': backend
            }
        
        return {
            'success': True,
            'backend': result.backend,
            'counts': result.counts,
            'probabilities': result.probabilities,
            'execution_time': result.execution_time,
            'metadata': result.metadata
        }
    
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'backend': backend
        }


@mcp.tool()
def execute_multi_backend(
    num_qubits: int,
    gates: list,
    backends: list,
    shots: int = 1000
) -> dict:
    """
    Execute the same circuit on multiple backends and compare results.
    
    Args:
        num_qubits: Number of qubits
        gates: Gate definitions
        backends: List of backends to execute on
        shots: Number of measurement shots
    
    Returns:
        Results from all backends with comparison metrics
    """
    results = {}
    errors = {}
    
    for backend_name in backends:
        if backend_name not in BACKENDS:
            errors[backend_name] = 'Backend not available'
            continue
        
        try:
            backend_obj = BACKENDS[backend_name]
            circuit_def = {'gates': gates, 'measure': True}
            circuit = backend_obj.create_circuit(num_qubits, circuit_def)
            result = backend_obj.execute_circuit(circuit, shots=shots)
            
            if result.error:
                errors[backend_name] = result.error
            else:
                results[backend_name] = {
                    'counts': result.counts,
                    'probabilities': result.probabilities,
                    'execution_time': result.execution_time
                }
        
        except Exception as e:
            errors[backend_name] = str(e)
    
    # Calculate comparison metrics
    comparison = {}
    if len(results) >= 2:
        backend_names = list(results.keys())
        for i, b1 in enumerate(backend_names):
            for b2 in backend_names[i+1:]:
                prob1 = results[b1]['probabilities']
                prob2 = results[b2]['probabilities']
                
                # Calculate fidelity-like metric
                all_states = set(prob1.keys()) | set(prob2.keys())
                similarity = sum(
                    min(prob1.get(state, 0), prob2.get(state, 0))
                    for state in all_states
                )
                
                comparison[f'{b1}_vs_{b2}'] = {
                    'similarity': similarity,
                    'time_ratio': results[b1]['execution_time'] / results[b2]['execution_time']
                }
    
    return {
        'results': results,
        'errors': errors,
        'comparison': comparison,
        'num_backends_executed': len(results),
        'metadata': {
            'num_qubits': num_qubits,
            'num_gates': len(gates),
            'shots': shots
        }
    }


@mcp.tool()
def create_bell_state(backend: str = 'qiskit', shots: int = 1000) -> dict:
    """
    Create and execute a Bell state (maximally entangled) circuit.
    
    Args:
        backend: Backend to use
        shots: Number of measurements
    
    Returns:
        Execution results
    """
    gates = [
        {'type': 'h', 'qubits': [0]},
        {'type': 'cx', 'qubits': [0, 1]}
    ]
    
    return execute_circuit(
        num_qubits=2,
        gates=gates,
        backend=backend,
        shots=shots
    )


@mcp.tool()
def create_ghz_state(num_qubits: int, backend: str = 'qiskit', shots: int = 1000) -> dict:
    """
    Create and execute a GHZ state (multi-qubit entangled state).
    
    Args:
        num_qubits: Number of qubits (>= 2)
        backend: Backend to use
        shots: Number of measurements
    
    Returns:
        Execution results
    """
    if num_qubits < 2:
        return {'error': 'GHZ state requires at least 2 qubits'}
    
    gates = [{'type': 'h', 'qubits': [0]}]
    
    # Add CNOT gates to entangle all qubits
    for i in range(1, num_qubits):
        gates.append({'type': 'cx', 'qubits': [0, i]})
    
    return execute_circuit(
        num_qubits=num_qubits,
        gates=gates,
        backend=backend,
        shots=shots
    )


@mcp.tool()
def quantum_teleportation(backend: str = 'qiskit', shots: int = 1000) -> dict:
    """
    Execute quantum teleportation protocol.
    
    Args:
        backend: Backend to use
        shots: Number of measurements
    
    Returns:
        Execution results
    """
    # 3-qubit teleportation circuit
    gates = [
        # Prepare Bell pair between qubits 1 and 2
        {'type': 'h', 'qubits': [1]},
        {'type': 'cx', 'qubits': [1, 2]},
        
        # Prepare state to teleport on qubit 0 (|+> state)
        {'type': 'h', 'qubits': [0]},
        
        # Bell measurement on qubits 0 and 1
        {'type': 'cx', 'qubits': [0, 1]},
        {'type': 'h', 'qubits': [0]},
    ]
    
    return execute_circuit(
        num_qubits=3,
        gates=gates,
        backend=backend,
        shots=shots
    )


@mcp.tool()
def benchmark_backends(
    circuit_type: str = 'bell',
    num_qubits: int = 2,
    shots: int = 1000
) -> dict:
    """
    Benchmark all available backends with a standard circuit.
    
    Args:
        circuit_type: Type of circuit ('bell', 'ghz', 'random')
        num_qubits: Number of qubits
        shots: Number of measurements
    
    Returns:
        Benchmark results for all backends
    """
    # Define circuit based on type
    if circuit_type == 'bell' and num_qubits == 2:
        gates = [
            {'type': 'h', 'qubits': [0]},
            {'type': 'cx', 'qubits': [0, 1]}
        ]
    elif circuit_type == 'ghz':
        gates = [{'type': 'h', 'qubits': [0]}]
        for i in range(1, num_qubits):
            gates.append({'type': 'cx', 'qubits': [0, i]})
    else:
        # Random circuit
        gates = []
        for i in range(num_qubits * 2):
            gates.append({'type': 'h', 'qubits': [i % num_qubits]})
            if i < num_qubits - 1:
                gates.append({'type': 'cx', 'qubits': [i % num_qubits, (i + 1) % num_qubits]})
    
    available_backends = [name for name, status in BACKEND_STATUS.items() if status]
    
    return execute_multi_backend(
        num_qubits=num_qubits,
        gates=gates,
        backends=[b for b in available_backends if b in BACKENDS],
        shots=shots
    )


@mcp.tool()
def get_circuit_qasm(
    num_qubits: int,
    gates: list,
    backend: str = 'qiskit'
) -> dict:
    """
    Generate QASM representation of a circuit without executing it.
    
    Args:
        num_qubits: Number of qubits
        gates: Gate definitions
        backend: Backend to use for QASM generation
    
    Returns:
        QASM string and circuit info
    """
    return create_circuit(num_qubits, gates, backend, measure=True)


if __name__ == "__main__":
    # Initialize backend status on startup
    check_backend_availability()
    print("Quantum Computing MCP Server initialized")
    print(f"Available backends: {list(BACKEND_STATUS.keys())}")
    
    # Run the server
    mcp.run()
