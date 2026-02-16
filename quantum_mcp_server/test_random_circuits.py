#!/usr/bin/env python3
"""
Generate 10 random 5-qubit circuits and test on all 4 backends
"""
import json
import subprocess
import time
import random
import math

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
    
    stdout, stderr = proc.communicate(input=input_data, timeout=20)
    
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

def generate_random_circuit(num_qubits: int, num_gates: int, seed: int) -> list:
    """Generate random quantum circuit"""
    random.seed(seed)
    gates = []
    
    # Single-qubit gates
    single_gates = ['h', 'x', 'y', 'z', 's', 't']
    
    # Two-qubit gates
    two_gates = ['cx', 'cz', 'swap']
    
    for _ in range(num_gates):
        # 70% single-qubit, 30% two-qubit
        if random.random() < 0.7:
            gate_type = random.choice(single_gates)
            qubit = random.randint(0, num_qubits - 1)
            gates.append({"type": gate_type, "qubits": [qubit]})
        else:
            gate_type = random.choice(two_gates)
            q1 = random.randint(0, num_qubits - 1)
            q2 = random.randint(0, num_qubits - 1)
            while q2 == q1:
                q2 = random.randint(0, num_qubits - 1)
            gates.append({"type": gate_type, "qubits": [q1, q2]})
    
    return gates

# Generate 10 random circuits
num_circuits = 10
num_qubits = 5
num_gates = 10
backends = ['qiskit', 'pennylane', 'cirq', 'pytket']

print("=" * 100)
print("RANDOM 5-QUBIT CIRCUIT TESTING")
print("=" * 100)
print(f"\nGenerating {num_circuits} random circuits with {num_qubits} qubits and {num_gates} gates each")
print(f"Testing on {len(backends)} backends: {', '.join(backends)}\n")

all_results = []

for circuit_num in range(1, num_circuits + 1):
    print(f"\n{'='*100}")
    print(f"Circuit #{circuit_num}")
    print('='*100)
    
    # Generate random circuit
    gates = generate_random_circuit(num_qubits, num_gates, seed=circuit_num * 42)
    
    # Show circuit description
    print(f"\nGate sequence ({len(gates)} gates):")
    gate_summary = {}
    for gate in gates:
        gate_type = gate['type'].upper()
        gate_summary[gate_type] = gate_summary.get(gate_type, 0) + 1
    
    summary_str = ", ".join([f"{count}x{gate}" for gate, count in sorted(gate_summary.items())])
    print(f"  {summary_str}")
    
    circuit_results = {
        'circuit_num': circuit_num,
        'gates': gates,
        'gate_summary': gate_summary,
        'backends': {}
    }
    
    # Run on all backends
    for backend in backends:
        print(f"\n  {backend:12s} ", end="", flush=True)
        
        try:
            result = run_mcp_tool("execute_circuit", {
                "num_qubits": num_qubits,
                "gates": gates,
                "backend": backend,
                "shots": 1000
            })
            
            if result.get('success'):
                exec_time = result.get('execution_time', 0) * 1000
                counts = result.get('counts', {})
                num_states = len(counts)
                
                # Get top 3 states
                top_states = sorted(counts.items(), key=lambda x: x[1], reverse=True)[:3]
                
                print(f"✓ {exec_time:6.2f}ms  |  {num_states:2d} states  |  ", end="")
                print(f"Top: {top_states[0][0]} ({top_states[0][1]}%)")
                
                circuit_results['backends'][backend] = {
                    'success': True,
                    'exec_time': exec_time,
                    'num_states': num_states,
                    'top_states': top_states,
                    'counts': counts
                }
            else:
                error_msg = result.get('error', 'Unknown')
                print(f"✗ Error: {error_msg}")
                circuit_results['backends'][backend] = {
                    'success': False,
                    'error': error_msg
                }
        except Exception as e:
            print(f"✗ Exception: {str(e)[:50]}")
            circuit_results['backends'][backend] = {
                'success': False,
                'error': str(e)
            }
    
    all_results.append(circuit_results)

# Generate summary statistics
print("\n" + "="*100)
print("SUMMARY STATISTICS")
print("="*100)

# Performance by backend
print("\nAverage Execution Time by Backend:")
for backend in backends:
    times = [r['backends'][backend]['exec_time'] 
             for r in all_results 
             if r['backends'][backend].get('success')]
    
    if times:
        avg_time = sum(times) / len(times)
        min_time = min(times)
        max_time = max(times)
        print(f"  {backend:12s}  Avg: {avg_time:6.2f}ms  |  Range: {min_time:6.2f}ms - {max_time:6.2f}ms")

# Success rate
print("\nSuccess Rate:")
for backend in backends:
    successes = sum(1 for r in all_results if r['backends'][backend].get('success'))
    rate = (successes / num_circuits) * 100
    print(f"  {backend:12s}  {successes}/{num_circuits} ({rate:.0f}%)")

# Complexity analysis
print("\nCircuit Complexity vs Performance:")
for circuit_num, result in enumerate(all_results, 1):
    total_gates = len(result['gates'])
    print(f"\n  Circuit #{circuit_num} ({total_gates} gates):")
    
    for backend in backends:
        if result['backends'][backend].get('success'):
            exec_time = result['backends'][backend]['exec_time']
            num_states = result['backends'][backend]['num_states']
            print(f"    {backend:12s}  {exec_time:6.2f}ms  ({num_states} output states)")

# State distribution analysis
print("\n" + "="*100)
print("STATE DISTRIBUTION ANALYSIS")
print("="*100)

for circuit_num, result in enumerate(all_results, 1):
    print(f"\nCircuit #{circuit_num}:")
    
    # Compare top state across backends
    print("  Most probable states by backend:")
    for backend in backends:
        if result['backends'][backend].get('success'):
            top_state, top_prob = result['backends'][backend]['top_states'][0]
            print(f"    {backend:12s}  |{top_state}⟩  ({top_prob}%)")

# Find fastest and slowest circuits
print("\n" + "="*100)
print("PERFORMANCE EXTREMES")
print("="*100)

# For each backend, find fastest and slowest
for backend in backends:
    times = [(i+1, r['backends'][backend]['exec_time']) 
             for i, r in enumerate(all_results) 
             if r['backends'][backend].get('success')]
    
    if times:
        fastest = min(times, key=lambda x: x[1])
        slowest = max(times, key=lambda x: x[1])
        
        print(f"\n{backend}:")
        print(f"  Fastest: Circuit #{fastest[0]} ({fastest[1]:.2f}ms)")
        print(f"  Slowest: Circuit #{slowest[0]} ({slowest[1]:.2f}ms)")
        print(f"  Speedup: {slowest[1]/fastest[1]:.2f}x difference")

print("\n" + "="*100)
print("✓ All random circuit tests completed!")
print("="*100)
