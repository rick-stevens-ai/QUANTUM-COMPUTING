# Quantum Computing MCP Server - Model Integration Guide

## Overview

This MCP server provides a unified interface to 5 quantum computing frameworks:
- **IBM Qiskit** - Industry-standard quantum SDK
- **Xanadu PennyLane** - Quantum machine learning
- **Google Cirq** - Google's quantum framework
- **Quantinuum PyTKET** - Advanced compiler and optimizer
- **Classiq** - High-level quantum algorithm design

## Quick Start

### Check Available Backends

```json
{
  "tool": "list_backends",
  "arguments": {}
}
```

**Returns:**
```json
{
  "total_backends": 5,
  "available_backends": 4,
  "backends": {
    "qiskit": {
      "available": true,
      "description": "IBM Qiskit with Aer Simulator",
      "version": "2.3.0"
    },
    ...
  }
}
```

## Core Operations

### 1. Create and Execute Simple Circuit

**Create a Bell State (2-qubit entanglement):**

```json
{
  "tool": "create_bell_state",
  "arguments": {
    "backend": "qiskit",
    "shots": 1000
  }
}
```

**Returns:**
```json
{
  "success": true,
  "backend": "qiskit",
  "counts": {
    "00": 501,
    "11": 499
  },
  "probabilities": {
    "00": 0.501,
    "11": 0.499
  },
  "execution_time": 0.045
}
```

### 2. Create Custom Circuit

**Define gates using standardized format:**

```json
{
  "tool": "execute_circuit",
  "arguments": {
    "num_qubits": 3,
    "gates": [
      {"type": "h", "qubits": [0]},
      {"type": "cx", "qubits": [0, 1]},
      {"type": "cx", "qubits": [1, 2]}
    ],
    "backend": "qiskit",
    "shots": 1000
  }
}
```

### 3. Multi-Backend Comparison

**Run same circuit on multiple backends:**

```json
{
  "tool": "execute_multi_backend",
  "arguments": {
    "num_qubits": 2,
    "gates": [
      {"type": "h", "qubits": [0]},
      {"type": "cx", "qubits": [0, 1]}
    ],
    "backends": ["qiskit", "pennylane", "cirq"],
    "shots": 1000
  }
}
```

**Returns comparison with similarity metrics:**
```json
{
  "results": {
    "qiskit": {
      "counts": {"00": 495, "11": 505},
      "execution_time": 0.042
    },
    "pennylane": {
      "counts": {"00": 498, "11": 502},
      "execution_time": 0.038
    }
  },
  "comparison": {
    "qiskit_vs_pennylane": {
      "similarity": 0.993,
      "time_ratio": 1.105
    }
  }
}
```

## Gate Reference

### Supported Gate Types

| Gate | Type String | Qubits | Parameters | Description |
|------|------------|--------|------------|-------------|
| Hadamard | `"h"` | 1 | None | Creates superposition |
| Pauli-X | `"x"` | 1 | None | Bit flip |
| Pauli-Y | `"y"` | 1 | None | Bit + phase flip |
| Pauli-Z | `"z"` | 1 | None | Phase flip |
| Rotation-X | `"rx"` | 1 | [angle] | Rotate around X-axis |
| Rotation-Y | `"ry"` | 1 | [angle] | Rotate around Y-axis |
| Rotation-Z | `"rz"` | 1 | [angle] | Rotate around Z-axis |
| CNOT | `"cx"` or `"cnot"` | 2 | None | Controlled-NOT |
| CZ | `"cz"` | 2 | None | Controlled-Z |
| SWAP | `"swap"` | 2 | None | Swap two qubits |
| Toffoli | `"ccx"` or `"toffoli"` | 3 | None | Controlled-Controlled-NOT |
| S Gate | `"s"` | 1 | None | Phase gate |
| T Gate | `"t"` | 1 | None | π/8 gate |

### Gate Definition Format

```json
{
  "type": "gate_name",
  "qubits": [qubit_indices],
  "params": [parameters]  // Optional
}
```

**Examples:**

```json
// Single-qubit gate
{"type": "h", "qubits": [0]}

// Two-qubit gate
{"type": "cx", "qubits": [0, 1]}

// Parametric gate
{"type": "rx", "qubits": [0], "params": [1.5708]}

// Three-qubit gate
{"type": "ccx", "qubits": [0, 1, 2]}
```

## Advanced Patterns

### Pattern 1: Quantum Superposition

Create superposition on all qubits:

```json
{
  "tool": "execute_circuit",
  "arguments": {
    "num_qubits": 4,
    "gates": [
      {"type": "h", "qubits": [0]},
      {"type": "h", "qubits": [1]},
      {"type": "h", "qubits": [2]},
      {"type": "h", "qubits": [3]}
    ],
    "backend": "qiskit",
    "shots": 2000
  }
}
```

**Expected:** Equal probability for all 16 basis states.

### Pattern 2: GHZ State (N-qubit entanglement)

```json
{
  "tool": "create_ghz_state",
  "arguments": {
    "num_qubits": 5,
    "backend": "qiskit",
    "shots": 1000
  }
}
```

**Expected:** Only |00000⟩ and |11111⟩ states.

### Pattern 3: Quantum Phase Estimation

```json
{
  "tool": "execute_circuit",
  "arguments": {
    "num_qubits": 4,
    "gates": [
      {"type": "h", "qubits": [0]},
      {"type": "h", "qubits": [1]},
      {"type": "h", "qubits": [2]},
      {"type": "x", "qubits": [3]},
      {"type": "cx", "qubits": [2, 3]},
      {"type": "cx", "qubits": [2, 3]},
      {"type": "cx", "qubits": [1, 3]},
      {"type": "cx", "qubits": [1, 3]},
      {"type": "cx", "qubits": [1, 3]},
      {"type": "cx", "qubits": [1, 3]},
      {"type": "cx", "qubits": [0, 3]}
    ],
    "backend": "qiskit",
    "shots": 1000
  }
}
```

### Pattern 4: QASM Input

If you have QASM from another source:

```json
{
  "tool": "execute_circuit",
  "arguments": {
    "qasm": "OPENQASM 2.0;\ninclude \"qelib1.inc\";\nqreg q[2];\ncreg c[2];\nh q[0];\ncx q[0],q[1];\nmeasure q[0] -> c[0];\nmeasure q[1] -> c[1];",
    "backend": "qiskit",
    "shots": 1000
  }
}
```

### Pattern 5: Get QASM Without Execution

Useful for debugging or circuit visualization:

```json
{
  "tool": "get_circuit_qasm",
  "arguments": {
    "num_qubits": 2,
    "gates": [
      {"type": "h", "qubits": [0]},
      {"type": "cx", "qubits": [0, 1]}
    ],
    "backend": "qiskit"
  }
}
```

**Returns:**
```json
{
  "success": true,
  "qasm": "OPENQASM 2.0;\ninclude \"qelib1.inc\";\nqreg q[2];\ncreg c[2];\nh q[0];\ncx q[0],q[1];\nmeasure q -> c;",
  "circuit_info": {
    "num_qubits": 2,
    "num_gates": 3,
    "depth": 2
  }
}
```

## Common Quantum Algorithms

### Algorithm 1: Quantum Teleportation

```json
{
  "tool": "quantum_teleportation",
  "arguments": {
    "backend": "qiskit",
    "shots": 1000
  }
}
```

### Algorithm 2: Deutsch-Jozsa (Constant Function)

```json
{
  "tool": "execute_circuit",
  "arguments": {
    "num_qubits": 3,
    "gates": [
      {"type": "x", "qubits": [2]},
      {"type": "h", "qubits": [0]},
      {"type": "h", "qubits": [1]},
      {"type": "h", "qubits": [2]},
      {"type": "h", "qubits": [0]},
      {"type": "h", "qubits": [1]}
    ],
    "backend": "qiskit",
    "shots": 100
  }
}
```

### Algorithm 3: Grover's Search (2-qubit)

```json
{
  "tool": "execute_circuit",
  "arguments": {
    "num_qubits": 2,
    "gates": [
      {"type": "h", "qubits": [0]},
      {"type": "h", "qubits": [1]},
      {"type": "cz", "qubits": [0, 1]},
      {"type": "h", "qubits": [0]},
      {"type": "h", "qubits": [1]},
      {"type": "x", "qubits": [0]},
      {"type": "x", "qubits": [1]},
      {"type": "cz", "qubits": [0, 1]},
      {"type": "x", "qubits": [0]},
      {"type": "x", "qubits": [1]},
      {"type": "h", "qubits": [0]},
      {"type": "h", "qubits": [1]}
    ],
    "backend": "qiskit",
    "shots": 1000
  }
}
```

## Benchmarking

### Compare Backend Performance

```json
{
  "tool": "benchmark_backends",
  "arguments": {
    "circuit_type": "ghz",
    "num_qubits": 4,
    "shots": 1000
  }
}
```

**Circuit Types:**
- `"bell"` - 2-qubit Bell state
- `"ghz"` - N-qubit GHZ state
- `"random"` - Random gate sequence

## Best Practices

### 1. Start Simple
Begin with small circuits (2-4 qubits) to validate your logic.

### 2. Use Multi-Backend for Validation
Run critical circuits on multiple backends to verify correctness:

```json
{
  "tool": "execute_multi_backend",
  "arguments": {
    "num_qubits": 2,
    "gates": [...],
    "backends": ["qiskit", "pennylane", "cirq"],
    "shots": 5000
  }
}
```

### 3. Check Similarity Metrics
When comparing backends, similarity > 0.95 indicates consistent results.

### 4. Adjust Shots for Precision
- Quick testing: 100-500 shots
- Standard: 1000 shots
- High precision: 5000-10000 shots

### 5. Backend Selection
- **Qiskit**: Best all-around, great for learning
- **PennyLane**: Best for ML integration
- **Cirq**: Best for Google-specific algorithms
- **PyTKET**: Best for optimization
- **Classiq**: Best for high-level algorithm design

## Error Handling

All tools return standardized responses:

**Success:**
```json
{
  "success": true,
  "backend": "qiskit",
  ...
}
```

**Failure:**
```json
{
  "success": false,
  "error": "Error description",
  "backend": "qiskit"
}
```

## Troubleshooting

### Backend Not Available
Check with `list_backends` tool first.

### Invalid Gate Type
Refer to Gate Reference section for supported gates.

### QASM Parse Error
Ensure QASM follows OpenQASM 2.0 specification.

### Timeout on Classiq
Classiq requires cloud authentication and may take longer.

## Example Workflows

### Workflow 1: Experiment and Compare

1. **Design circuit** with `get_circuit_qasm`
2. **Test on single backend** with `execute_circuit`
3. **Compare across backends** with `execute_multi_backend`
4. **Analyze results** using similarity metrics

### Workflow 2: Algorithm Development

1. **Start with known algorithm** (Bell, GHZ, etc.)
2. **Modify gates incrementally**
3. **Validate each modification** on preferred backend
4. **Benchmark final circuit** on all backends

### Workflow 3: Learning Quantum Computing

1. **List backends** to see what's available
2. **Try pre-built circuits** (Bell, GHZ, teleportation)
3. **Experiment with gate types** one at a time
4. **Build up complexity** gradually

## Quick Reference

| Task | Tool | Key Arguments |
|------|------|---------------|
| List backends | `list_backends` | None |
| Execute circuit | `execute_circuit` | `num_qubits`, `gates`, `backend`, `shots` |
| Compare backends | `execute_multi_backend` | `num_qubits`, `gates`, `backends` |
| Bell state | `create_bell_state` | `backend`, `shots` |
| GHZ state | `create_ghz_state` | `num_qubits`, `backend` |
| Teleportation | `quantum_teleportation` | `backend`, `shots` |
| Get QASM | `get_circuit_qasm` | `num_qubits`, `gates` |
| Benchmark | `benchmark_backends` | `circuit_type`, `num_qubits` |

## Support

For issues or questions about specific backends, refer to their official documentation:
- Qiskit: https://qiskit.org/documentation/
- PennyLane: https://pennylane.ai/
- Cirq: https://quantumai.google/cirq
- PyTKET: https://cqcl.github.io/pytket/
- Classiq: https://docs.classiq.io/

---

**Version:** 1.0  
**Last Updated:** February 2026  
**Supported Backends:** Qiskit, PennyLane, Cirq, PyTKET, Classiq
