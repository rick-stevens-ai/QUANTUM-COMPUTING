#!/usr/bin/env python3
"""
Test 3 quantum algorithms on all 4 backends
"""
import json
import subprocess
import time
from typing import Dict, List

def run_mcp_tool(tool_name: str, arguments: dict) -> dict:
    """Execute MCP tool and return result"""
    messages = [
        {"jsonrpc":"2.0","id":1,"method":"initialize","params":{
            "protocolVersion":"2024-11-05","capabilities":{},
            "clientInfo":{"name":"test","version":"1.0"}}},
        {"jsonrpc":"2.0","id":2,"method":"notifications/initialized"},
        {"jsonrpc":"2.0","id":3,"method":"tools/call","params":{
            "name":tool_name,"arguments":arguments}}
    ]
    
    input_data = '\n'.join(json.dumps(m) for m in messages)
    
    proc = subprocess.Popen(
        ['/home/stevens/QUANTUM-COMPUTING/quantum_mcp_server/run_mcp_server.sh'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    stdout, stderr = proc.communicate(input=input_data, timeout=15)
    
    for line in stdout.strip().split('\n'):
        try:
            obj = json.loads(line)
            if obj.get('id') == 3 and 'result' in obj:
                result = obj['result']
                if result.get('content'):
                    return json.loads(result['content'][0]['text'])
        except json.JSONDecodeError:
            continue
    
    return {"error": "No valid response"}

# Algorithm 1: Deutsch-Jozsa (constant function)
def deutsch_jozsa_constant(backend: str) -> dict:
    """Deutsch-Jozsa with constant oracle (should measure |00>)"""
    gates = [
        {"type": "x", "qubits": [1]},      # Prepare |1> on ancilla
        {"type": "h", "qubits": [0]},      # Hadamard on input
        {"type": "h", "qubits": [1]},      # Hadamard on ancilla
        # Oracle for constant function: do nothing (identity)
        {"type": "h", "qubits": [0]},      # Final Hadamard
    ]
    return run_mcp_tool("execute_circuit", {
        "num_qubits": 2,
        "gates": gates,
        "backend": backend,
        "shots": 100
    })

# Algorithm 2: Grover's Search (2 qubits, search for |11>)
def grovers_search(backend: str) -> dict:
    """Grover's algorithm to find |11> state"""
    gates = [
        # Initialize superposition
        {"type": "h", "qubits": [0]},
        {"type": "h", "qubits": [1]},
        
        # Oracle: mark |11> with phase flip
        {"type": "cz", "qubits": [0, 1]},
        
        # Diffusion operator
        {"type": "h", "qubits": [0]},
        {"type": "h", "qubits": [1]},
        {"type": "x", "qubits": [0]},
        {"type": "x", "qubits": [1]},
        {"type": "cz", "qubits": [0, 1]},
        {"type": "x", "qubits": [0]},
        {"type": "x", "qubits": [1]},
        {"type": "h", "qubits": [0]},
        {"type": "h", "qubits": [1]},
    ]
    return run_mcp_tool("execute_circuit", {
        "num_qubits": 2,
        "gates": gates,
        "backend": backend,
        "shots": 100
    })

# Algorithm 3: Quantum Fourier Transform (3 qubits)
def qft_3qubit(backend: str) -> dict:
    """3-qubit Quantum Fourier Transform on |001> state"""
    import math
    
    gates = [
        # Prepare initial state |001>
        {"type": "x", "qubits": [2]},
        
        # QFT
        {"type": "h", "qubits": [0]},
        {"type": "cp", "qubits": [1, 0], "params": [math.pi/2]},
        {"type": "cp", "qubits": [2, 0], "params": [math.pi/4]},
        
        {"type": "h", "qubits": [1]},
        {"type": "cp", "qubits": [2, 1], "params": [math.pi/2]},
        
        {"type": "h", "qubits": [2]},
        
        # Swap qubits to reverse order
        {"type": "swap", "qubits": [0, 2]},
    ]
    return run_mcp_tool("execute_circuit", {
        "num_qubits": 3,
        "gates": gates,
        "backend": backend,
        "shots": 100
    })

# Run all tests
backends = ['qiskit', 'pennylane', 'cirq', 'pytket']
algorithms = [
    ("Deutsch-Jozsa", deutsch_jozsa_constant),
    ("Grover Search", grovers_search),
    ("QFT (3-qubit)", qft_3qubit)
]

print("=" * 80)
print("QUANTUM ALGORITHM COMPARISON")
print("=" * 80)

results = {}

for algo_name, algo_func in algorithms:
    print(f"\n{'='*80}")
    print(f"Algorithm: {algo_name}")
    print('='*80)
    
    results[algo_name] = {}
    
    for backend in backends:
        print(f"\n  Testing on {backend}...", end=" ", flush=True)
        
        start = time.time()
        result = algo_func(backend)
        total_time = time.time() - start
        
        if result.get('success'):
            exec_time = result.get('execution_time', 0) * 1000
            counts = result.get('counts', {})
            
            # Get top measurement
            top_state = max(counts.items(), key=lambda x: x[1]) if counts else ("", 0)
            
            print(f"✓")
            print(f"    Execution: {exec_time:.2f}ms (total: {total_time*1000:.0f}ms)")
            print(f"    Top result: |{top_state[0]}⟩ ({top_state[1]}%)")
            print(f"    Distribution: {counts}")
            
            results[algo_name][backend] = {
                'success': True,
                'exec_time': exec_time,
                'total_time': total_time * 1000,
                'counts': counts,
                'top_state': top_state[0],
                'top_prob': top_state[1]
            }
        else:
            error = result.get('error', 'Unknown error')
            print(f"✗ {error}")
            results[algo_name][backend] = {'success': False, 'error': error}

# Summary comparison
print("\n" + "="*80)
print("PERFORMANCE SUMMARY")
print("="*80)

for algo_name in results:
    print(f"\n{algo_name}:")
    
    # Collect execution times
    times = []
    for backend in backends:
        if results[algo_name][backend].get('success'):
            exec_time = results[algo_name][backend]['exec_time']
            times.append((backend, exec_time))
    
    if times:
        times.sort(key=lambda x: x[1])
        print("  Speed ranking:")
        for rank, (backend, exec_time) in enumerate(times, 1):
            emoji = "⚡" if rank == 1 else "  "
            print(f"    {rank}. {backend:12s} {exec_time:6.2f}ms {emoji}")

# Accuracy comparison
print("\n" + "="*80)
print("ACCURACY COMPARISON")
print("="*80)

print("\nDeutsch-Jozsa (should measure |00> for constant function):")
for backend in backends:
    if results["Deutsch-Jozsa"][backend].get('success'):
        counts = results["Deutsch-Jozsa"][backend]['counts']
        zero_prob = counts.get('00', counts.get('00 00', counts.get('00 00 00', 0)))
        print(f"  {backend:12s} |00⟩: {zero_prob}%")

print("\nGrover's Search (should find |11> with high probability):")
for backend in backends:
    if results["Grover Search"][backend].get('success'):
        counts = results["Grover Search"][backend]['counts']
        target_prob = counts.get('11', counts.get('11 11', counts.get('11 00 00', 0)))
        print(f"  {backend:12s} |11⟩: {target_prob}%")

print("\nQFT results (complex superposition expected):")
for backend in backends:
    if results["QFT (3-qubit)"][backend].get('success'):
        counts = results["QFT (3-qubit)"][backend]['counts']
        num_states = len(counts)
        print(f"  {backend:12s} {num_states} different states measured")

print("\n" + "="*80)
print("✓ All algorithm tests completed!")
print("="*80)
