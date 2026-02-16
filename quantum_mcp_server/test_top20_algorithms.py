#!/usr/bin/env python3
"""
Top 20 Quantum Algorithms - Cross-Backend Test Suite
=====================================================
Tests 20 fundamental quantum algorithms across all 4 backends:
  Qiskit, PennyLane, Cirq, PyTKET

Each algorithm is defined as a circuit spec (name, num_qubits, gates)
with a verification function that checks measurement results.

Usage:
    python3 test_top20_algorithms.py
"""

import math
import sys
import time
from typing import Dict, List, Callable, Any, Optional

# ---------------------------------------------------------------------------
# Import backends
# ---------------------------------------------------------------------------
sys.path.insert(0, '/home/stevens/QUANTUM-COMPUTING')

from quantum_mcp_server.backends.qiskit_backend import QiskitBackend
from quantum_mcp_server.backends.pennylane_backend import PennyLaneBackend
from quantum_mcp_server.backends.cirq_backend import CirqBackend
from quantum_mcp_server.backends.pytket_backend import PyTKETBackend

BACKENDS = {
    'qiskit': QiskitBackend,
    'pennylane': PennyLaneBackend,
    'cirq': CirqBackend,
    'pytket': PyTKETBackend,
}

SHOTS = 1000

# ===========================================================================
# Helper utilities
# ===========================================================================

def top_states(counts: Dict[str, int], n: int = 3) -> str:
    """Return top-n states as a compact string."""
    total = sum(counts.values())
    sorted_c = sorted(counts.items(), key=lambda x: -x[1])[:n]
    parts = [f"|{s}> {100*c/total:.0f}%" for s, c in sorted_c]
    return ", ".join(parts)


def dominant_prob(counts: Dict[str, int], state: str) -> float:
    """Return probability of *state* in counts (0.0-1.0)."""
    total = sum(counts.values())
    return counts.get(state, 0) / total if total else 0.0


def states_present(counts: Dict[str, int]) -> set:
    """Return set of states that appeared."""
    return set(counts.keys())


# ===========================================================================
# Algorithm definitions  (each returns a dict with keys:
#   name, category, num_qubits, gates, verify(counts)->bool )
# ===========================================================================

def algo_deutsch_jozsa_constant() -> dict:
    """1. Deutsch-Jozsa: constant oracle => input qubit measures 0."""
    gates = [
        {"type": "x", "qubits": [1]},
        {"type": "h", "qubits": [0]},
        {"type": "h", "qubits": [1]},
        # constant oracle: identity (do nothing)
        {"type": "h", "qubits": [0]},
    ]

    def verify(counts):
        # qubit-0 should always be 0 -> states matching ?0 pattern
        total = sum(counts.values())
        zero_count = sum(v for k, v in counts.items() if k[0] == '0')
        return zero_count / total >= 0.90

    return dict(name="Deutsch-Jozsa (constant)", category="Oracular",
                num_qubits=2, gates=gates, verify=verify)


def algo_deutsch_jozsa_balanced() -> dict:
    """2. Deutsch-Jozsa: balanced oracle on 3 qubits => input qubits non-zero."""
    gates = [
        {"type": "x", "qubits": [2]},
        {"type": "h", "qubits": [0]},
        {"type": "h", "qubits": [1]},
        {"type": "h", "qubits": [2]},
        # balanced oracle: CNOT from each input to ancilla
        {"type": "cx", "qubits": [0, 2]},
        {"type": "cx", "qubits": [1, 2]},
        {"type": "h", "qubits": [0]},
        {"type": "h", "qubits": [1]},
    ]

    def verify(counts):
        # input qubits (bits 0,1) should be '11' with high probability
        total = sum(counts.values())
        # bit positions: state string is q0 q1 q2
        hit = sum(v for k, v in counts.items() if k[:2] == '11')
        return hit / total >= 0.90

    return dict(name="Deutsch-Jozsa (balanced)", category="Oracular",
                num_qubits=3, gates=gates, verify=verify)


def algo_bernstein_vazirani() -> dict:
    """3. Bernstein-Vazirani: secret string s=1011."""
    # 5 qubits: 4 input + 1 ancilla (qubit 4)
    s = "1011"
    gates = []
    # prepare ancilla
    gates.append({"type": "x", "qubits": [4]})
    # Hadamard all
    for i in range(5):
        gates.append({"type": "h", "qubits": [i]})
    # Oracle: CNOT from qubit i to ancilla where s[i]='1'
    for i, bit in enumerate(s):
        if bit == '1':
            gates.append({"type": "cx", "qubits": [i, 4]})
    # Hadamard on input qubits
    for i in range(4):
        gates.append({"type": "h", "qubits": [i]})

    def verify(counts):
        total = sum(counts.values())
        # input qubits should read '1011'
        hit = sum(v for k, v in counts.items() if k[:4] == '1011')
        return hit / total >= 0.90

    return dict(name="Bernstein-Vazirani (s=1011)", category="Oracular",
                num_qubits=5, gates=gates, verify=verify)


def algo_simons() -> dict:
    """4. Simon's Algorithm: s=11 on 4 qubits (2 input + 2 output)."""
    gates = []
    # Hadamard on input qubits
    gates.append({"type": "h", "qubits": [0]})
    gates.append({"type": "h", "qubits": [1]})
    # Oracle for f with period s=11: copy input to output, then XOR with s
    # f(x) = x XOR s if x >= s, else x  (simplified: just copy + conditional flip)
    # Standard oracle: CNOT input->output, then CNOT q0->q3, q1->q3 for the period
    gates.append({"type": "cx", "qubits": [0, 2]})
    gates.append({"type": "cx", "qubits": [1, 3]})
    # XOR with s=11 conditioned on q0
    gates.append({"type": "cx", "qubits": [0, 3]})
    gates.append({"type": "cx", "qubits": [0, 2]})
    # Hadamard on input
    gates.append({"type": "h", "qubits": [0]})
    gates.append({"type": "h", "qubits": [1]})

    def verify(counts):
        total = sum(counts.values())
        # input qubits should measure either 00 or 11 (orthogonal to s=11)
        hit = sum(v for k, v in counts.items() if k[:2] in ('00', '11'))
        return hit / total >= 0.90

    return dict(name="Simon's Algorithm (s=11)", category="Oracular",
                num_qubits=4, gates=gates, verify=verify)


def algo_grover_2qubit() -> dict:
    """5. Grover's Search: 2-qubit, target |11>."""
    gates = [
        {"type": "h", "qubits": [0]},
        {"type": "h", "qubits": [1]},
        # Oracle: phase-flip |11>
        {"type": "cz", "qubits": [0, 1]},
        # Diffusion
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

    def verify(counts):
        return dominant_prob(counts, '11') >= 0.90

    return dict(name="Grover's Search (2-qubit)", category="Search",
                num_qubits=2, gates=gates, verify=verify)


def algo_grover_3qubit() -> dict:
    """6. Grover's Search: 3-qubit, target |101>."""
    gates = []
    # Initialize superposition
    for i in range(3):
        gates.append({"type": "h", "qubits": [i]})

    # One Grover iteration
    # Oracle for |101>: flip q1, Toffoli(q0,q1,q2 as control->phase), flip q1
    # Use ancilla-free phase oracle: X on q1, then CCZ via H-CCX-H, then X on q1
    gates.append({"type": "x", "qubits": [1]})
    # CCZ = H on target, CCX, H on target
    gates.append({"type": "h", "qubits": [2]})
    gates.append({"type": "ccx", "qubits": [0, 1, 2]})
    gates.append({"type": "h", "qubits": [2]})
    gates.append({"type": "x", "qubits": [1]})

    # Diffusion operator
    for i in range(3):
        gates.append({"type": "h", "qubits": [i]})
    for i in range(3):
        gates.append({"type": "x", "qubits": [i]})
    gates.append({"type": "h", "qubits": [2]})
    gates.append({"type": "ccx", "qubits": [0, 1, 2]})
    gates.append({"type": "h", "qubits": [2]})
    for i in range(3):
        gates.append({"type": "x", "qubits": [i]})
    for i in range(3):
        gates.append({"type": "h", "qubits": [i]})

    def verify(counts):
        return dominant_prob(counts, '101') >= 0.70

    return dict(name="Grover's Search (3-qubit, |101>)", category="Search",
                num_qubits=3, gates=gates, verify=verify)


def algo_qft_3qubit() -> dict:
    """7. QFT on 3 qubits starting from |001>."""
    gates = [
        {"type": "x", "qubits": [2]},  # prepare |001>
        # QFT
        {"type": "h", "qubits": [0]},
        {"type": "cp", "qubits": [1, 0], "params": [math.pi / 2]},
        {"type": "cp", "qubits": [2, 0], "params": [math.pi / 4]},
        {"type": "h", "qubits": [1]},
        {"type": "cp", "qubits": [2, 1], "params": [math.pi / 2]},
        {"type": "h", "qubits": [2]},
        {"type": "swap", "qubits": [0, 2]},
    ]

    def verify(counts):
        # QFT of a computational basis state -> ~uniform distribution over 8 states
        n_states = len(counts)
        return n_states >= 5  # at least 5 of 8 states observed

    return dict(name="QFT (3-qubit)", category="Fourier",
                num_qubits=3, gates=gates, verify=verify)


def algo_inverse_qft() -> dict:
    """8. Inverse QFT: apply QFT then inverse QFT to recover |001>."""
    gates = [
        {"type": "x", "qubits": [2]},  # prepare |001>
        # QFT
        {"type": "h", "qubits": [0]},
        {"type": "cp", "qubits": [1, 0], "params": [math.pi / 2]},
        {"type": "cp", "qubits": [2, 0], "params": [math.pi / 4]},
        {"type": "h", "qubits": [1]},
        {"type": "cp", "qubits": [2, 1], "params": [math.pi / 2]},
        {"type": "h", "qubits": [2]},
        {"type": "swap", "qubits": [0, 2]},
        # Inverse QFT
        {"type": "swap", "qubits": [0, 2]},
        {"type": "h", "qubits": [2]},
        {"type": "cp", "qubits": [2, 1], "params": [-math.pi / 2]},
        {"type": "h", "qubits": [1]},
        {"type": "cp", "qubits": [2, 0], "params": [-math.pi / 4]},
        {"type": "cp", "qubits": [1, 0], "params": [-math.pi / 2]},
        {"type": "h", "qubits": [0]},
    ]

    def verify(counts):
        return dominant_prob(counts, '001') >= 0.90

    return dict(name="Inverse QFT (3-qubit)", category="Fourier",
                num_qubits=3, gates=gates, verify=verify)


def algo_qpe_t_gate() -> dict:
    """9. Quantum Phase Estimation for T gate (phase = pi/4 => 1/8).
    3 counting qubits + 1 eigenstate qubit.
    Expected counting register: 001 (= 1/8 of 2^3 = 1)."""
    gates = []
    # Prepare eigenstate |1> on qubit 3
    gates.append({"type": "x", "qubits": [3]})
    # Hadamard on counting qubits
    for i in range(3):
        gates.append({"type": "h", "qubits": [i]})
    # Controlled-U^(2^k) operations
    # T gate = phase pi/4, T^1 on counting qubit 2
    gates.append({"type": "cp", "qubits": [2, 3], "params": [math.pi / 4]})
    # T^2 = S gate on counting qubit 1
    gates.append({"type": "cp", "qubits": [1, 3], "params": [math.pi / 2]})
    # T^4 = Z gate on counting qubit 0
    gates.append({"type": "cp", "qubits": [0, 3], "params": [math.pi]})
    # Inverse QFT on counting qubits (0,1,2)
    gates.append({"type": "swap", "qubits": [0, 2]})
    gates.append({"type": "h", "qubits": [2]})
    gates.append({"type": "cp", "qubits": [2, 1], "params": [-math.pi / 2]})
    gates.append({"type": "h", "qubits": [1]})
    gates.append({"type": "cp", "qubits": [2, 0], "params": [-math.pi / 4]})
    gates.append({"type": "cp", "qubits": [1, 0], "params": [-math.pi / 2]})
    gates.append({"type": "h", "qubits": [0]})

    def verify(counts):
        total = sum(counts.values())
        # counting register = first 3 bits, should be '001'
        hit = sum(v for k, v in counts.items() if k[:3] == '001')
        return hit / total >= 0.80

    return dict(name="QPE (T gate, phase=pi/4)", category="Fourier",
                num_qubits=4, gates=gates, verify=verify)


def algo_bell_states() -> dict:
    """10. All four Bell states: |Phi+>, |Phi->, |Psi+>, |Psi->."""
    # We create |Phi+> = (|00>+|11>)/sqrt(2)
    gates = [
        {"type": "h", "qubits": [0]},
        {"type": "cx", "qubits": [0, 1]},
    ]

    def verify(counts):
        total = sum(counts.values())
        p00 = counts.get('00', 0) / total
        p11 = counts.get('11', 0) / total
        # should be ~50/50 between 00 and 11
        return (p00 >= 0.35 and p11 >= 0.35 and
                p00 + p11 >= 0.95)

    return dict(name="Bell State (Phi+)", category="Entanglement",
                num_qubits=2, gates=gates, verify=verify)


def algo_ghz_5qubit() -> dict:
    """11. GHZ state: 5-qubit (|00000>+|11111>)/sqrt(2)."""
    gates = [{"type": "h", "qubits": [0]}]
    for i in range(4):
        gates.append({"type": "cx", "qubits": [i, i + 1]})

    def verify(counts):
        total = sum(counts.values())
        p0 = counts.get('00000', 0) / total
        p1 = counts.get('11111', 0) / total
        return (p0 >= 0.35 and p1 >= 0.35 and p0 + p1 >= 0.95)

    return dict(name="GHZ State (5-qubit)", category="Entanglement",
                num_qubits=5, gates=gates, verify=verify)


def algo_w_state() -> dict:
    """12. W state: (|001>+|010>+|100>)/sqrt(3)."""
    # Verified construction:
    # 1. Ry on q2 to create sqrt(2/3)|000> + sqrt(1/3)|001>
    # 2. CRy(pi/2) controlled by q2=0 on q1 -> adds |010> branch
    # 3. Toffoli (q1=0 AND q2=0) flips q0 -> converts |000> to |100>
    theta_w = 2 * math.asin(1 / math.sqrt(3))
    gates = [
        # Step 1: amplitude split on q2
        {"type": "ry", "qubits": [2], "params": [theta_w]},
        # Step 2: CRy(pi/2) on q1 controlled by q2=0
        # Decomposed: X(q2), Ry(pi/4,q1), CX(q2,q1), Ry(-pi/4,q1), CX(q2,q1), X(q2)
        {"type": "x", "qubits": [2]},
        {"type": "ry", "qubits": [1], "params": [math.pi / 4]},
        {"type": "cx", "qubits": [2, 1]},
        {"type": "ry", "qubits": [1], "params": [-math.pi / 4]},
        {"type": "cx", "qubits": [2, 1]},
        {"type": "x", "qubits": [2]},
        # Step 3: flip q0 when q1=0 AND q2=0
        {"type": "x", "qubits": [1]},
        {"type": "x", "qubits": [2]},
        {"type": "ccx", "qubits": [1, 2, 0]},
        {"type": "x", "qubits": [2]},
        {"type": "x", "qubits": [1]},
    ]

    def verify(counts):
        total = sum(counts.values())
        p001 = counts.get('001', 0) / total
        p010 = counts.get('010', 0) / total
        p100 = counts.get('100', 0) / total
        valid = p001 + p010 + p100
        # Each should be ~33%, total ~100%
        return (valid >= 0.85 and
                p001 >= 0.15 and p010 >= 0.15 and p100 >= 0.15)

    return dict(name="W State (3-qubit)", category="Entanglement",
                num_qubits=3, gates=gates, verify=verify)


def algo_teleportation() -> dict:
    """13. Quantum Teleportation: teleport |1> from q0 to q2."""
    gates = [
        # Prepare state to teleport: |1> on q0
        {"type": "x", "qubits": [0]},
        # Create Bell pair between q1 and q2
        {"type": "h", "qubits": [1]},
        {"type": "cx", "qubits": [1, 2]},
        # Bell measurement on q0, q1
        {"type": "cx", "qubits": [0, 1]},
        {"type": "h", "qubits": [0]},
        # Conditional corrections (classically controlled, but we apply both)
        {"type": "cx", "qubits": [1, 2]},
        {"type": "cz", "qubits": [0, 2]},
    ]

    def verify(counts):
        total = sum(counts.values())
        # q2 (last bit) should be 1
        hit = sum(v for k, v in counts.items() if k[-1] == '1')
        return hit / total >= 0.90

    return dict(name="Quantum Teleportation", category="Communication",
                num_qubits=3, gates=gates, verify=verify)


def algo_superdense_coding() -> dict:
    """14. Superdense Coding: encode '10' using one qubit."""
    gates = [
        # Create Bell pair
        {"type": "h", "qubits": [0]},
        {"type": "cx", "qubits": [0, 1]},
        # Alice encodes '10': apply Z to her qubit (q0)
        # Encoding: I->00, X->01, Z->10, XZ->11
        {"type": "z", "qubits": [0]},
        # Bob decodes: reverse Bell circuit
        {"type": "cx", "qubits": [0, 1]},
        {"type": "h", "qubits": [0]},
    ]

    def verify(counts):
        return dominant_prob(counts, '10') >= 0.90

    return dict(name="Superdense Coding (encode 10)", category="Communication",
                num_qubits=2, gates=gates, verify=verify)


def algo_bit_flip_correction() -> dict:
    """15. Bit-Flip Error Correction: encode, flip, correct."""
    # 3 data qubits (0,1,2) + 2 syndrome qubits (3,4)
    gates = [
        # Prepare |1> state on q0
        {"type": "x", "qubits": [0]},
        # Encode: spread q0 to q1, q2
        {"type": "cx", "qubits": [0, 1]},
        {"type": "cx", "qubits": [0, 2]},
        # Error: bit flip on q0
        {"type": "x", "qubits": [0]},
        # Syndrome extraction
        {"type": "cx", "qubits": [0, 3]},
        {"type": "cx", "qubits": [1, 3]},
        {"type": "cx", "qubits": [1, 4]},
        {"type": "cx", "qubits": [2, 4]},
        # Correction: Toffoli to flip q0 if syndrome = 11 (both ancillas set)
        # syndrome 10 on (q3,q4) means q0 flipped
        # For simplicity: correct q0 based on syndrome
        {"type": "ccx", "qubits": [3, 4, 1]},  # if both set, flip q1 (wrong syndrome combo)
        # Actually, let's use direct correction:
        # Syndrome q3=1,q4=0 => q0 error -> flip q0
        # We need: X on q4, Toffoli(q3,q4,q0), X on q4
        {"type": "x", "qubits": [4]},
        {"type": "ccx", "qubits": [3, 4, 0]},
        {"type": "x", "qubits": [4]},
        # Undo the wrong Toffoli above (q3,q4,q1)
        {"type": "ccx", "qubits": [3, 4, 1]},
    ]

    def verify(counts):
        total = sum(counts.values())
        # data qubits (0,1,2) should read 111 (corrected back to encoded |1>)
        hit = sum(v for k, v in counts.items() if k[:3] == '111')
        return hit / total >= 0.85

    return dict(name="Bit-Flip Error Correction", category="Error Correction",
                num_qubits=5, gates=gates, verify=verify)


def algo_phase_flip_correction() -> dict:
    """16. Phase-Flip Error Correction: encode in Hadamard basis, flip, correct."""
    # Same as bit-flip but in Hadamard basis
    # 3 data qubits (0,1,2) + 2 syndrome qubits (3,4)
    gates = [
        # Prepare |+> state
        {"type": "h", "qubits": [0]},
        # Encode in Hadamard basis
        {"type": "cx", "qubits": [0, 1]},
        {"type": "cx", "qubits": [0, 2]},
        {"type": "h", "qubits": [0]},
        {"type": "h", "qubits": [1]},
        {"type": "h", "qubits": [2]},
        # Phase flip error on q0
        {"type": "z", "qubits": [0]},
        # Decode from Hadamard basis for syndrome
        {"type": "h", "qubits": [0]},
        {"type": "h", "qubits": [1]},
        {"type": "h", "qubits": [2]},
        # Syndrome extraction (same as bit-flip)
        {"type": "cx", "qubits": [0, 3]},
        {"type": "cx", "qubits": [1, 3]},
        {"type": "cx", "qubits": [1, 4]},
        {"type": "cx", "qubits": [2, 4]},
        # Correct q0
        {"type": "x", "qubits": [4]},
        {"type": "ccx", "qubits": [3, 4, 0]},
        {"type": "x", "qubits": [4]},
    ]

    def verify(counts):
        total = sum(counts.values())
        # After correction, data qubits should all agree
        hit = sum(v for k, v in counts.items() if k[:3] in ('000', '111'))
        return hit / total >= 0.80

    return dict(name="Phase-Flip Error Correction", category="Error Correction",
                num_qubits=5, gates=gates, verify=verify)


def algo_vqe_ansatz() -> dict:
    """17. VQE Ansatz (H2-like): parameterized circuit at theta=pi/4."""
    theta = math.pi / 4
    gates = [
        # Hartree-Fock initial state
        {"type": "x", "qubits": [0]},
        # UCCSD-like ansatz
        {"type": "ry", "qubits": [0], "params": [theta]},
        {"type": "ry", "qubits": [1], "params": [-theta]},
        {"type": "cx", "qubits": [0, 1]},
        {"type": "ry", "qubits": [0], "params": [theta / 2]},
        {"type": "ry", "qubits": [1], "params": [-theta / 2]},
    ]

    def verify(counts):
        # Should produce a valid probability distribution
        total = sum(counts.values())
        return total >= SHOTS * 0.95 and len(counts) >= 2

    return dict(name="VQE Ansatz (H2-like)", category="Variational",
                num_qubits=2, gates=gates, verify=verify)


def algo_qaoa_maxcut() -> dict:
    """18. QAOA MaxCut: 4-node ring graph, p=1."""
    gamma = math.pi / 4
    beta = math.pi / 8
    gates = []
    # Initial superposition
    for i in range(4):
        gates.append({"type": "h", "qubits": [i]})
    # Cost layer: ZZ interaction for each edge of ring (0-1, 1-2, 2-3, 3-0)
    edges = [(0, 1), (1, 2), (2, 3), (3, 0)]
    for (i, j) in edges:
        gates.append({"type": "cx", "qubits": [i, j]})
        gates.append({"type": "rz", "qubits": [j], "params": [2 * gamma]})
        gates.append({"type": "cx", "qubits": [i, j]})
    # Mixer layer: RX on each qubit
    for i in range(4):
        gates.append({"type": "rx", "qubits": [i], "params": [2 * beta]})

    def verify(counts):
        total = sum(counts.values())
        # MaxCut solutions for ring: 0101 and 1010 should be elevated
        p0101 = counts.get('0101', 0) / total
        p1010 = counts.get('1010', 0) / total
        combined = p0101 + p1010
        # They should be more likely than uniform (1/16 = 6.25% each)
        return combined >= 0.15

    return dict(name="QAOA MaxCut (4-node ring)", category="Variational",
                num_qubits=4, gates=gates, verify=verify)


def algo_half_adder() -> dict:
    """19. Quantum Half Adder: 1+1 = sum=0, carry=1."""
    # q0=A, q1=B, q2=sum, q3=carry
    gates = [
        # Set inputs: A=1, B=1
        {"type": "x", "qubits": [0]},
        {"type": "x", "qubits": [1]},
        # Carry = A AND B (Toffoli)
        {"type": "ccx", "qubits": [0, 1, 3]},
        # Sum = A XOR B (two CNOTs)
        {"type": "cx", "qubits": [0, 2]},
        {"type": "cx", "qubits": [1, 2]},
    ]

    def verify(counts):
        total = sum(counts.values())
        # Expected: A=1, B=1, sum=0, carry=1 => '1101'
        return dominant_prob(counts, '1101') >= 0.90

    return dict(name="Quantum Half Adder (1+1)", category="Arithmetic",
                num_qubits=4, gates=gates, verify=verify)


def algo_trotter_ising() -> dict:
    """20. Trotterized Ising Simulation: 2-qubit with 3 Trotter steps."""
    dt = 0.3  # time step
    J = 1.0   # coupling
    h_field = 0.5  # transverse field

    gates = []
    # Initial state: |++> (both in superposition)
    gates.append({"type": "h", "qubits": [0]})
    gates.append({"type": "h", "qubits": [1]})

    # 3 Trotter steps
    for _ in range(3):
        # ZZ interaction: exp(-i J dt ZZ)
        gates.append({"type": "cx", "qubits": [0, 1]})
        gates.append({"type": "rz", "qubits": [1], "params": [2 * J * dt]})
        gates.append({"type": "cx", "qubits": [0, 1]})
        # Transverse field: exp(-i h dt X) on each qubit
        gates.append({"type": "rx", "qubits": [0], "params": [2 * h_field * dt]})
        gates.append({"type": "rx", "qubits": [1], "params": [2 * h_field * dt]})

    def verify(counts):
        # Non-trivial evolution should produce multiple states
        total = sum(counts.values())
        return total >= SHOTS * 0.95 and len(counts) >= 2

    return dict(name="Trotterized Ising (2-qubit)", category="Simulation",
                num_qubits=2, gates=gates, verify=verify)


# ===========================================================================
# All 20 algorithms
# ===========================================================================

ALL_ALGORITHMS = [
    algo_deutsch_jozsa_constant,     # 1
    algo_deutsch_jozsa_balanced,     # 2
    algo_bernstein_vazirani,         # 3
    algo_simons,                     # 4
    algo_grover_2qubit,              # 5
    algo_grover_3qubit,              # 6
    algo_qft_3qubit,                 # 7
    algo_inverse_qft,                # 8
    algo_qpe_t_gate,                 # 9
    algo_bell_states,                # 10
    algo_ghz_5qubit,                 # 11
    algo_w_state,                    # 12
    algo_teleportation,              # 13
    algo_superdense_coding,          # 14
    algo_bit_flip_correction,        # 15
    algo_phase_flip_correction,      # 16
    algo_vqe_ansatz,                 # 17
    algo_qaoa_maxcut,                # 18
    algo_half_adder,                 # 19
    algo_trotter_ising,              # 20
]

# ===========================================================================
# Main test runner
# ===========================================================================

def run_algorithm(backend_name: str, backend_instance, spec: dict) -> dict:
    """Run a single algorithm on a single backend. Returns result dict."""
    try:
        circuit_def = {'gates': spec['gates'], 'measure': True}
        circuit = backend_instance.create_circuit(spec['num_qubits'], circuit_def)
        start = time.time()
        result = backend_instance.execute_circuit(circuit, shots=SHOTS)
        elapsed = time.time() - start

        if result.error:
            return {'pass': False, 'error': result.error, 'time_ms': 0}

        counts = result.counts
        passed = spec['verify'](counts)
        return {
            'pass': passed,
            'counts': counts,
            'time_ms': elapsed * 1000,
            'top': top_states(counts),
        }
    except Exception as e:
        return {'pass': False, 'error': str(e), 'time_ms': 0}


def main():
    print("=" * 100)
    print("  TOP 20 QUANTUM ALGORITHMS - CROSS-BACKEND TEST SUITE")
    print("  Backends: Qiskit | PennyLane | Cirq | PyTKET")
    print(f"  Shots per test: {SHOTS}")
    print("=" * 100)

    # Instantiate backends
    backend_instances = {}
    for name, cls in BACKENDS.items():
        try:
            backend_instances[name] = cls()
            print(f"  [{name:10s}] Loaded OK")
        except Exception as e:
            print(f"  [{name:10s}] FAILED to load: {e}")

    backend_names = list(backend_instances.keys())
    print()

    # Header
    col_w = 14
    hdr = f"{'#':>3} {'Algorithm':<38} {'Category':<16}"
    for bn in backend_names:
        hdr += f" {bn:^{col_w}}"
    hdr += f"  {'Top States'}"
    print(hdr)
    print("-" * len(hdr))

    total_pass = 0
    total_fail = 0
    total_error = 0
    results_grid = []

    for idx, algo_fn in enumerate(ALL_ALGORITHMS, 1):
        spec = algo_fn()
        row_results = {}
        row_line = f"{idx:>3} {spec['name']:<38} {spec['category']:<16}"
        any_top = ""

        for bn in backend_names:
            if bn not in backend_instances:
                row_line += f" {'SKIP':^{col_w}}"
                continue

            r = run_algorithm(bn, backend_instances[bn], spec)
            row_results[bn] = r

            if 'error' in r:
                row_line += f" {'ERROR':^{col_w}}"
                total_error += 1
            elif r['pass']:
                ms = r['time_ms']
                row_line += f" {'PASS':^{col_w}}"
                total_pass += 1
                if not any_top:
                    any_top = r['top']
            else:
                row_line += f" {'FAIL':^{col_w}}"
                total_fail += 1
                if not any_top:
                    any_top = r.get('top', '')

        row_line += f"  {any_top}"
        print(row_line)
        results_grid.append((spec, row_results))

    # Summary
    total = total_pass + total_fail + total_error
    print()
    print("=" * 100)
    print(f"  SUMMARY: {total_pass}/{total} PASSED, {total_fail} FAILED, {total_error} ERRORS")
    print("=" * 100)

    # Timing summary per backend
    print(f"\n  {'Backend':<12} {'Avg (ms)':>10} {'Min (ms)':>10} {'Max (ms)':>10} {'Pass':>6} {'Fail':>6}")
    print(f"  {'-'*60}")
    for bn in backend_names:
        times = []
        bp = bf = 0
        for spec, row in results_grid:
            r = row.get(bn)
            if r:
                if r.get('time_ms', 0) > 0:
                    times.append(r['time_ms'])
                if 'error' in r:
                    bf += 1
                elif r['pass']:
                    bp += 1
                else:
                    bf += 1
        if times:
            avg_t = sum(times) / len(times)
            print(f"  {bn:<12} {avg_t:>10.1f} {min(times):>10.1f} {max(times):>10.1f} {bp:>6} {bf:>6}")
        else:
            print(f"  {bn:<12} {'N/A':>10} {'N/A':>10} {'N/A':>10} {bp:>6} {bf:>6}")

    # Detail on failures
    failures = []
    for spec, row in results_grid:
        for bn in backend_names:
            r = row.get(bn)
            if r and not r.get('pass', False):
                err = r.get('error', '')
                top = r.get('top', 'N/A')
                failures.append((spec['name'], bn, err if err else f"verification failed: {top}"))

    if failures:
        print(f"\n  FAILURE DETAILS:")
        print(f"  {'-'*80}")
        for name, bn, detail in failures:
            print(f"  {name} [{bn}]: {detail[:80]}")

    print()
    return total_pass, total_fail, total_error


if __name__ == '__main__':
    p, f, e = main()
    sys.exit(0 if f == 0 and e == 0 else 1)
