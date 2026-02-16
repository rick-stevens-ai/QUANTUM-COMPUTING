# Quantum Programs You Can Run

## Basic Quantum Circuits

### 1. Bell State / EPR Pair (2 qubits)
**Purpose:** Maximum quantum entanglement between 2 qubits
```
Gates: H(0), CNOT(0,1)
Result: |00⟩ + |11⟩ (superposition of both qubits correlated)
```

### 2. GHZ State (N qubits)
**Purpose:** Multi-qubit entanglement
```
Gates: H(0), CNOT(0,1), CNOT(0,2), ... CNOT(0,N-1)
Result: |000...⟩ + |111...⟩ (all qubits maximally entangled)
```

### 3. W State (N qubits)
**Purpose:** Different type of multi-qubit entanglement
```
More complex gate sequence
Result: |100...⟩ + |010...⟩ + |001...⟩ + ...
```

## Quantum Algorithms

### 4. Quantum Fourier Transform (QFT)
**Purpose:** Quantum analog of Fast Fourier Transform
**Applications:** Period finding, phase estimation
```
Uses Hadamard gates and controlled phase rotations
Required for Shor's algorithm
```

### 5. Grover's Search Algorithm
**Purpose:** Search unsorted database in O(√N) time vs classical O(N)
**Speedup:** Quadratic speedup
```
- Initialize superposition (H gates on all qubits)
- Apply oracle (marks solution)
- Apply diffusion operator (amplifies marked state)
- Repeat ~√N times
- Measure
```

### 6. Quantum Phase Estimation (QPE)
**Purpose:** Estimate eigenvalues of unitary operators
**Applications:** Core subroutine for many algorithms
```
- Prepare eigenstate
- Apply controlled-U operations
- Apply inverse QFT
- Measure phase
```

### 7. Variational Quantum Eigensolver (VQE)
**Purpose:** Find ground state energy of molecules/materials
**Applications:** Quantum chemistry, materials science
```
- Parameterized quantum circuit (ansatz)
- Classical optimizer adjusts parameters
- Measures energy expectation value
- Iterates until convergence
```
**Best Backend:** PennyLane (designed for quantum ML/VQE)

### 8. Quantum Approximate Optimization Algorithm (QAOA)
**Purpose:** Solve combinatorial optimization problems
**Applications:** Max-Cut, traveling salesman, scheduling
```
- Problem encoded in Hamiltonian
- Alternating problem and mixer Hamiltonians
- Classical optimizer finds best parameters
- p layers (depth parameter)
```

## Quantum Communication Protocols

### 9. Quantum Teleportation
**Purpose:** Transfer quantum state using entanglement
```
- Prepare Bell pair shared between Alice & Bob
- Alice performs Bell measurement on her qubit + state to teleport
- Alice sends 2 classical bits to Bob
- Bob applies correction based on classical bits
- Bob now has the original quantum state
```

### 10. Superdense Coding
**Purpose:** Send 2 classical bits using 1 qubit + entanglement
```
- Shared Bell pair
- Alice encodes 2 bits by applying gates
- Sends her qubit to Bob
- Bob measures both qubits and extracts 2 bits
```

## Quantum Error Correction

### 11. 3-Qubit Bit Flip Code
**Purpose:** Protect against bit flip errors
```
- Encode 1 logical qubit into 3 physical qubits
- Apply CNOT gates for encoding
- Can detect and correct single bit flip
```

### 12. Shor's 9-Qubit Code
**Purpose:** Protect against arbitrary single-qubit errors
```
- Encode 1 logical qubit into 9 physical qubits
- Protects against bit flip and phase flip errors
```

## Famous Quantum Algorithms

### 13. Deutsch-Jozsa Algorithm
**Purpose:** Determine if function is constant or balanced
**Speedup:** Exponential (1 query vs 2^(n-1) + 1 classical queries)
```
- Initialize |0...0⟩|1⟩
- Apply H gates
- Apply oracle
- Apply H gates
- Measure
```

### 14. Bernstein-Vazirani Algorithm
**Purpose:** Find hidden string s where f(x) = s·x
**Speedup:** Exponential (1 query vs n classical queries)
```
- Similar structure to Deutsch-Jozsa
- Oracle encodes hidden string
- Single measurement reveals entire string
```

### 15. Simon's Algorithm
**Purpose:** Find period of function
**Speedup:** Exponential
```
- Key inspiration for Shor's algorithm
- Uses quantum parallelism
```

### 16. Shor's Factoring Algorithm
**Purpose:** Factor large numbers efficiently
**Speedup:** Exponential (breaks RSA encryption)
**Limitation:** Requires many qubits (2n+3 for n-bit number)
```
- Choose random a < N
- Use QPE to find period r of a^x mod N
- Classical post-processing extracts factors
```
**Challenge:** Would need 4000+ qubits for RSA-2048

## Quantum Machine Learning

### 17. Quantum Neural Networks (QNN)
**Purpose:** ML on quantum hardware
**Best Backend:** PennyLane
```
- Parameterized quantum circuits
- Classical optimization of parameters
- Can learn nonlinear patterns
```

### 18. Quantum Kernel Methods
**Purpose:** Quantum feature maps for classification
```
- Map classical data to quantum states
- Compute inner products (kernel values)
- Use with classical SVM
```

### 19. Quantum Boltzmann Machines
**Purpose:** Generative modeling
```
- Quantum version of classical RBM
- Sample from quantum distributions
```

## Quantum Simulation

### 20. Hamiltonian Simulation
**Purpose:** Simulate time evolution of quantum systems
**Applications:** Chemistry, condensed matter physics
```
- Represent Hamiltonian H
- Approximate e^(-iHt) with Trotter decomposition
- Apply gate sequence
```

### 21. Molecular Ground State
**Purpose:** Find lowest energy configuration of molecules
**Applications:** Drug discovery, catalysis
```
- Map fermions to qubits (Jordan-Wigner, Bravyi-Kitaev)
- Use VQE or phase estimation
- Compute energy expectation values
```

## Benchmark Circuits

### 22. Quantum Volume Circuits
**Purpose:** Benchmark quantum computer capability
```
- Random unitary operations
- Increasing depth and width
- Measures effective quantum volume
```

### 23. Randomized Benchmarking
**Purpose:** Characterize gate fidelity
```
- Apply random Clifford gates
- Measure average fidelity
- Extrapolate error rates
```

## Current Simulator Capabilities

### Gate Support (All backends)
- **Single-qubit:** X, Y, Z, H (Hadamard), S, T, RX, RY, RZ
- **Two-qubit:** CNOT, CZ, SWAP, controlled rotations
- **Three-qubit:** Toffoli (CCX), Fredkin (CSWAP)
- **Measurement:** Computational basis, Pauli basis

### Qubit Limits
- **Qiskit:** ~30 qubits (simulator limitation)
- **PennyLane:** ~20 qubits (default device)
- **Cirq:** ~20-30 qubits
- **PyTKET:** ~20-30 qubits

### Special Capabilities
- **PennyLane:** Best for VQE, QML, hybrid classical-quantum
- **Cirq:** Google-style circuits, native support for their gates
- **PyTKET:** Best compiler optimization, high-level circuit manipulation
- **Qiskit:** Most mature ecosystem, extensive algorithm library

## What You CANNOT Run (Simulator Limitations)

❌ **Large Shor's Algorithm** - Needs thousands of qubits for meaningful RSA breaking
❌ **Fault-Tolerant Circuits** - Requires error correction (too many qubits)
❌ **Real Quantum Advantage** - Classical simulation catches up around 50 qubits
❌ **Noisy Intermediate-Scale Quantum (NISQ)** - Simulators are noise-free by default

## Getting Started

Start with simple circuits and progressively increase complexity:
1. Bell states → GHZ states (test entanglement)
2. Deutsch-Jozsa → Bernstein-Vazirani (simple algorithms)
3. Grover's search (2-3 qubits)
4. VQE on H2 molecule (quantum chemistry)
5. Small QAOA instances (optimization)
