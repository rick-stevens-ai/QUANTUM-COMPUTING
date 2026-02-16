# Installing Quantum MCP Server in Warp

## Configuration for Warp

### Option 1: Copy-Paste Configuration (Recommended)

Copy this JSON configuration and paste it into your Warp MCP settings:

```json
{
  "mcpServers": {
    "quantum-simulator": {
      "command": "python3",
      "args": [
        "/home/stevens/QUANTUM-COMPUTING/quantum_mcp_server/server.py"
      ],
      "env": {
        "PYTHONPATH": "/home/stevens/QUANTUM-COMPUTING/quantum_mcp_server"
      }
    }
  }
}
```

### Option 2: Use Configuration File

The configuration is also saved in: `warp_mcp_config.json`

You can reference it in your Warp settings.

## Server Details

- **Server Name**: `quantum-simulator`
- **Transport**: stdio (FastMCP default)
- **Command**: `python3`
- **Script**: `/home/stevens/QUANTUM-COMPUTING/quantum_mcp_server/server.py`
- **Environment**: Python 3.13

## Available MCP Tools

Once installed in Warp, you'll have access to these 9 tools:

1. **list_backends** - Check which quantum backends are available
2. **create_circuit** - Build quantum circuits from gate definitions
3. **execute_circuit** - Run quantum circuits on simulators
4. **execute_multi_backend** - Compare results across multiple backends
5. **get_circuit_qasm** - Export circuits to QASM format
6. **create_bell_state** - Quick Bell state creation
7. **create_ghz_state** - Multi-qubit GHZ states
8. **quantum_teleportation** - Teleportation protocol
9. **benchmark_backends** - Performance comparison

## Usage in Warp

### Example 1: Check Available Backends

```
Use the list_backends tool
```

### Example 2: Create a Bell State

```
Use create_bell_state with backend=qiskit and shots=1000
```

### Example 3: Custom Circuit

```
Use execute_circuit with:
- num_qubits: 3
- gates: [
    {"type": "h", "qubits": [0]},
    {"type": "cx", "qubits": [0, 1]},
    {"type": "cx", "qubits": [0, 2]}
  ]
- backend: qiskit
- shots: 1000
```

## Verification

After installation, test the server:

```bash
cd /home/stevens/QUANTUM-COMPUTING/quantum_mcp_server
python3 test_server.py
```

Expected output: All tests passing ✓

## Troubleshooting

### Server Doesn't Start

1. **Check Python version:**
   ```bash
   python3 --version  # Should be 3.13+
   ```

2. **Verify dependencies:**
   ```bash
   python3 -c "import fastmcp, qiskit; print('OK')"
   ```

3. **Check server directly:**
   ```bash
   python3 /home/stevens/QUANTUM-COMPUTING/quantum_mcp_server/server.py
   ```

### Tools Not Showing Up

1. Restart Warp
2. Check MCP settings are saved correctly
3. Verify the path in configuration is correct

### Import Errors

Make sure PYTHONPATH is set correctly in the configuration:
```json
"env": {
  "PYTHONPATH": "/home/stevens/QUANTUM-COMPUTING/quantum_mcp_server"
}
```

## Documentation

For complete usage guide, see:
- **MCP_HOWTO.md** - Comprehensive guide for AI models
- **README.md** - Technical documentation
- **DEPLOYMENT.md** - Deployment guide

## Quick Reference Card

| What You Want | MCP Tool | Key Parameters |
|---------------|----------|----------------|
| List available backends | `list_backends` | None |
| Create Bell state | `create_bell_state` | backend, shots |
| Run custom circuit | `execute_circuit` | num_qubits, gates, backend |
| Compare backends | `execute_multi_backend` | num_qubits, gates, backends |
| Get QASM | `get_circuit_qasm` | num_qubits, gates |

## Gate Format Reference

All gates use this format:
```json
{
  "type": "gate_name",
  "qubits": [indices],
  "params": [values]  // Optional, for parametric gates
}
```

**Common Gates:**
- `"h"` - Hadamard
- `"x"`, `"y"`, `"z"` - Pauli gates
- `"cx"` - CNOT (2 qubits)
- `"rx"`, `"ry"`, `"rz"` - Rotations (with params)

## Support

- Full how-to: `MCP_HOWTO.md`
- Issues: Check `DEPLOYMENT.md` troubleshooting
- Backend status: Run `test_all_frameworks_complete.py` in parent directory

---

**Server Location**: `/home/stevens/QUANTUM-COMPUTING/quantum_mcp_server`  
**Configuration File**: `warp_mcp_config.json`  
**Status**: ✅ Ready for Warp Integration
