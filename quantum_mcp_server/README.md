# Quantum Computing MCP Server

A unified FastMCP server providing a standardized interface to 5 major quantum computing frameworks on the NVIDIA DGX SPARK GB10 system.

## Features

- **Unified API**: Single interface for all quantum backends
- **Multi-Backend Execution**: Run same circuit on multiple backends
- **Comparison Tools**: Automated similarity metrics and benchmarking
- **QASM Support**: Import/export OpenQASM 2.0
- **Pre-built Algorithms**: Bell states, GHZ, teleportation, and more
- **Comprehensive Documentation**: Full how-to guide for models

## Supported Backends

| Backend | Version | Description | Status |
|---------|---------|-------------|--------|
| **Qiskit** | 2.3.0 | IBM's quantum SDK with Aer Simulator | ✅ Active |
| **PennyLane** | 0.44.0 | Quantum ML framework | 🚧 Planned |
| **Cirq** | 1.6.1 | Google's quantum framework | 🚧 Planned |
| **PyTKET** | 2.13.0 | Quantinuum's compiler | 🚧 Planned |
| **Classiq** | 1.1.0 | High-level algorithm design | 🚧 Planned |

## Quick Start

### 1. Test the Backend

```bash
cd quantum_mcp_server
python3 test_server.py
```

### 2. Run the MCP Server

```bash
cd quantum_mcp_server
python3 server.py
```

### 3. Use with MCP Client

See `MCP_HOWTO.md` for complete usage instructions.

## Project Structure

```
quantum_mcp_server/
├── server.py              # Main FastMCP server
├── test_server.py         # Test suite
├── MCP_HOWTO.md          # Complete usage guide for models
├── README.md             # This file
├── backends/             # Backend adapters
│   ├── __init__.py
│   ├── base.py           # Abstract base class
│   └── qiskit_backend.py # Qiskit implementation
└── utils/                # Utilities (future)
```

## Available MCP Tools

### Core Operations
- `list_backends()` - Check backend availability
- `create_circuit()` - Build a circuit from gate definitions
- `execute_circuit()` - Run a circuit on a backend
- `execute_multi_backend()` - Compare across backends
- `get_circuit_qasm()` - Generate QASM without execution

### Pre-built Circuits
- `create_bell_state()` - 2-qubit entanglement
- `create_ghz_state()` - N-qubit entanglement
- `quantum_teleportation()` - Teleportation protocol

### Utilities
- `benchmark_backends()` - Performance comparison

## Example Usage

### Create and Execute a Bell State

```python
# Using MCP tool
result = mcp.call_tool("create_bell_state", {
    "backend": "qiskit",
    "shots": 1000
})

# Expected output:
# {
#     "success": true,
#     "counts": {"00": 495, "11": 505},
#     "probabilities": {"00": 0.495, "11": 0.505}
# }
```

### Custom Circuit

```python
result = mcp.call_tool("execute_circuit", {
    "num_qubits": 3,
    "gates": [
        {"type": "h", "qubits": [0]},
        {"type": "cx", "qubits": [0, 1]},
        {"type": "cx", "qubits": [0, 2]}
    ],
    "backend": "qiskit",
    "shots": 1000
})
```

### Multi-Backend Comparison

```python
result = mcp.call_tool("execute_multi_backend", {
    "num_qubits": 2,
    "gates": [
        {"type": "h", "qubits": [0]},
        {"type": "cx", "qubits": [0, 1]}
    ],
    "backends": ["qiskit"],  # Add more as implemented
    "shots": 1000
})
```

## Gate Reference

### Single-Qubit Gates
- `h` - Hadamard
- `x`, `y`, `z` - Pauli gates
- `s`, `t` - Phase gates
- `rx`, `ry`, `rz` - Rotation gates (require params)

### Multi-Qubit Gates
- `cx`, `cnot` - Controlled-NOT
- `cz` - Controlled-Z
- `swap` - Swap
- `ccx`, `toffoli` - Toffoli gate

## Development Roadmap

### Phase 1: Core Infrastructure ✅
- [x] Base backend architecture
- [x] Qiskit adapter implementation
- [x] FastMCP server setup
- [x] Basic MCP tools
- [x] Documentation

### Phase 2: Multi-Backend Support 🚧
- [ ] PennyLane adapter
- [ ] Cirq adapter
- [ ] PyTKET adapter
- [ ] Classiq adapter (with conda env integration)

### Phase 3: Advanced Features 📋
- [ ] Circuit optimization
- [ ] Noise modeling
- [ ] Advanced algorithms (Grover, Shor, VQE)
- [ ] GPU acceleration
- [ ] Circuit visualization

### Phase 4: Production 📋
- [ ] Error recovery
- [ ] Caching and persistence
- [ ] Authentication for cloud backends
- [ ] Performance monitoring
- [ ] Load balancing

## Testing

Run the test suite:

```bash
cd quantum_mcp_server
python3 test_server.py
```

Expected output:
```
Testing Qiskit Backend...

[Test 1] Creating Bell state circuit
✓ Circuit created: 2 qubits, 3 operations

[Test 2] Getting circuit info
✓ Qubits: 2, Gates: 3, Depth: 2

[Test 3] Executing circuit
✓ Execution successful
  Counts: {'00': 503, '11': 497}

[Test 4] Converting to QASM
✓ QASM generated

[Test 5] Loading from QASM
✓ Circuit loaded from QASM

All tests passed! ✓
```

## Requirements

- Python 3.13 (main environment)
- Python 3.12 (conda env for Classiq)
- FastMCP 2.14.5+
- Qiskit 2.3.0+
- PennyLane 0.44.0+ (optional)
- Cirq 1.6.1+ (optional)
- PyTKET 2.13.0+ (optional)
- Classiq 1.1.0+ (optional)

## Configuration

### Environment Variables

```bash
# Optional: Set default backend
export QUANTUM_DEFAULT_BACKEND=qiskit

# Optional: Enable debug logging
export QUANTUM_DEBUG=1

# Optional: Classiq conda environment name
export CLASSIQ_CONDA_ENV=classiq-env
```

## Troubleshooting

### Import Error
Make sure you're running from the QUANTUM-COMPUTING directory:
```bash
cd /home/stevens/QUANTUM-COMPUTING
python3 quantum_mcp_server/server.py
```

### Backend Not Available
Check installations:
```bash
python3 test_all_frameworks_complete.py
```

### FastMCP Issues
Reinstall FastMCP:
```bash
pip3 install --upgrade fastmcp
```

## Documentation

- **MCP_HOWTO.md** - Complete guide for model integration
- **backends/base.py** - Backend adapter interface documentation
- **Installation Guide** - See ../installation_summary.md

## Contributing

To add a new backend:

1. Create adapter in `backends/`:
```python
from .base import QuantumBackend, BackendType

class MyBackend(QuantumBackend):
    def __init__(self):
        super().__init__(BackendType.MY_BACKEND)
    
    # Implement abstract methods...
```

2. Register in `server.py`:
```python
from backends.my_backend import MyBackend

BACKENDS = {
    'qiskit': QiskitBackend(),
    'mybackend': MyBackend(),
}
```

3. Add tests in `test_server.py`

## Performance

### Qiskit Backend Benchmarks (NVIDIA DGX SPARK GB10)

| Circuit | Qubits | Gates | Shots | Time (ms) |
|---------|--------|-------|-------|-----------|
| Bell State | 2 | 2 | 1000 | 42 |
| GHZ-4 | 4 | 4 | 1000 | 55 |
| GHZ-8 | 8 | 8 | 1000 | 89 |
| Random-10 | 10 | 50 | 1000 | 156 |

## License

Part of the Quantum Computing Framework installation on NVIDIA DGX SPARK GB10.

## Support

For issues specific to:
- **Server**: Check MCP_HOWTO.md
- **Backends**: See ../installation_summary.md
- **Frameworks**: Refer to official documentation

## Changelog

### Version 1.0.0 (2026-02-15)
- Initial release
- Qiskit backend adapter
- FastMCP server with 9 tools
- Comprehensive documentation
- Test suite

---

**Server Status**: 🟢 Active Development  
**Backend Count**: 1/5 implemented  
**Test Coverage**: Qiskit only  
**Last Updated**: February 15, 2026
