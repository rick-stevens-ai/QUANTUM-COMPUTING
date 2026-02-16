# Quantum Computing MCP Server - Development Environment

This directory contains a complete quantum computing development environment with **all 5 major quantum frameworks** installed and tested on the NVIDIA DGX SPARK GB10.

## ✅ Installation Status

All 5 frameworks successfully installed and tested:

1. **IBM Qiskit** 2.3.0 ✓
2. **Xanadu PennyLane** 0.44.0 ✓
3. **Google Cirq** 1.6.1 ✓
4. **Quantinuum PyTKET** 2.13.0 ✓
5. **Classiq** 1.1.0 ✓

## 🚀 Quick Start

### Automated Installation
```bash
chmod +x install.sh && ./install.sh
# Options: --skip-classiq, --dry-run, --help
```

### Test All Frameworks
```bash
python3 test_all_frameworks_complete.py
```

### Run Top 20 Algorithm Test Suite
```bash
python3 quantum_mcp_server/test_top20_algorithms.py
```
Tests 20 quantum algorithms across all 4 backends (Qiskit, PennyLane, Cirq, PyTKET) = 80 test combinations.

### Test Individual Frameworks
```bash
python3 test_qiskit.py
python3 test_pennylane.py
python3 test_cirq.py
python3 test_pytket.py
conda run -n classiq-env python test_classiq_simple.py  # Classiq (Python 3.12)
```

## 🧪 Algorithm Test Suite

The test suite (`quantum_mcp_server/test_top20_algorithms.py`) covers 20 fundamental algorithms:

| # | Algorithm | Category |
|---|-----------|----------|
| 1-4 | Deutsch-Jozsa, Bernstein-Vazirani, Simon's | Oracular |
| 5-6 | Grover's Search (2/3-qubit) | Search |
| 7-9 | QFT, Inverse QFT, QPE | Fourier |
| 10-12 | Bell States, GHZ, W State | Entanglement |
| 13-14 | Teleportation, Superdense Coding | Communication |
| 15-16 | Bit-Flip / Phase-Flip Error Correction | Error Correction |
| 17-18 | VQE Ansatz, QAOA MaxCut | Variational |
| 19 | Quantum Half Adder | Arithmetic |
| 20 | Trotterized Ising Simulation | Simulation |

## 📁 Files

### Documentation
- `README.md` - This file
- `installation_summary.md` - Detailed installation documentation
- `install.sh` - Automated installation script

### Test Scripts
- `test_all_frameworks_complete.py` - Complete test suite (all 5 frameworks)
- `quantum_mcp_server/test_top20_algorithms.py` - Top 20 algorithms x 4 backends
- `test_qiskit.py` / `test_pennylane.py` / `test_cirq.py` / `test_pytket.py` - Individual framework tests
- `test_classiq_simple.py` - Classiq installation test

## 🔧 Environment Details

### Python Environments
- **Main**: Python 3.13.11 (Qiskit, PennyLane, Cirq, PyTKET)
- **Classiq**: Python 3.12.12 in conda env `classiq-env`

### System Specs
- **Platform**: NVIDIA DGX SPARK GB10
- **CPU**: ARM Grace (20 cores)
- **GPU**: NVIDIA GB10 (Blackwell)
- **RAM**: 119 GB
- **CUDA**: 13.0

## 💡 Usage Examples

### Activate Classiq Environment
```bash
conda activate classiq-env
python test_classiq_simple.py
conda deactivate
```

### Run Framework Tests
```bash
# Test everything
python3 test_all_frameworks_complete.py

# Individual tests return detailed output
python3 test_qiskit.py
```

## 📝 Next Steps

Ready to build the quantum computing MCP server with:
1. Unified API across all 5 frameworks
2. Backend abstraction layer
3. Circuit translation between frameworks
4. Multi-environment execution support
5. GPU acceleration (where supported)
6. Cloud authentication (Classiq)

## 📚 Framework Documentation

- [Qiskit](https://qiskit.org/documentation/)
- [PennyLane](https://pennylane.ai/)
- [Cirq](https://quantumai.google/cirq)
- [PyTKET](https://cqcl.github.io/pytket/)
- [Classiq](https://docs.classiq.io/)

---

**Status**: ✅ All frameworks installed and tested  
**Date**: February 15, 2026  
**System**: NVIDIA DGX SPARK GB10
