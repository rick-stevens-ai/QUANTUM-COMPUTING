#!/usr/bin/env bash
# ===========================================================================
# Quantum Computing MCP Server - Automated Installation Script
# ===========================================================================
# Installs all quantum computing frameworks and the MCP server on
# NVIDIA DGX SPARK GB10 (ARM aarch64).
#
# Frameworks installed:
#   1. IBM Qiskit 2.3.0 + Aer Simulator
#   2. Xanadu PennyLane 0.44.0 + Lightning Qubit
#   3. Google Cirq 1.6.1
#   4. Quantinuum PyTKET 2.13.0 + pytket-qiskit
#   5. FastMCP (latest)
#   6. Classiq 1.1.0 (separate conda env, optional)
#
# Usage:
#   chmod +x install.sh && ./install.sh
#   ./install.sh --skip-classiq   # Skip Classiq (requires conda)
#   ./install.sh --dry-run        # Show what would be installed
# ===========================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="${SCRIPT_DIR}/install.log"
CLASSIQ_CONDA_ENV="classiq-env"
SKIP_CLASSIQ=false
DRY_RUN=false

# ---------------------------------------------------------------------------
# Color output
# ---------------------------------------------------------------------------
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

info()    { echo -e "${BLUE}[INFO]${NC}  $*" | tee -a "$LOG_FILE"; }
ok()      { echo -e "${GREEN}[  OK]${NC}  $*" | tee -a "$LOG_FILE"; }
warn()    { echo -e "${YELLOW}[WARN]${NC}  $*" | tee -a "$LOG_FILE"; }
fail()    { echo -e "${RED}[FAIL]${NC}  $*" | tee -a "$LOG_FILE"; }
section() { echo -e "\n${CYAN}========== $* ==========${NC}" | tee -a "$LOG_FILE"; }

# ---------------------------------------------------------------------------
# Parse arguments
# ---------------------------------------------------------------------------
for arg in "$@"; do
    case "$arg" in
        --skip-classiq) SKIP_CLASSIQ=true ;;
        --dry-run)      DRY_RUN=true ;;
        --help|-h)
            echo "Usage: $0 [--skip-classiq] [--dry-run] [--help]"
            echo "  --skip-classiq  Skip Classiq installation (requires conda)"
            echo "  --dry-run       Show what would be installed without installing"
            echo "  --help          Show this help message"
            exit 0
            ;;
        *) warn "Unknown argument: $arg" ;;
    esac
done

# ---------------------------------------------------------------------------
# Pre-flight checks
# ---------------------------------------------------------------------------
section "Pre-flight Checks"

: > "$LOG_FILE"  # truncate log
info "Log file: $LOG_FILE"
info "Working directory: $SCRIPT_DIR"

# Python version check
PYTHON_CMD=""
for cmd in python3 python; do
    if command -v "$cmd" &>/dev/null; then
        PYTHON_CMD="$cmd"
        break
    fi
done

if [[ -z "$PYTHON_CMD" ]]; then
    fail "Python not found. Please install Python 3.10+."
    exit 1
fi

PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | grep -oP '\d+\.\d+')
PYTHON_MAJOR=$(echo "$PYTHON_VERSION" | cut -d. -f1)
PYTHON_MINOR=$(echo "$PYTHON_VERSION" | cut -d. -f2)

if (( PYTHON_MAJOR < 3 || (PYTHON_MAJOR == 3 && PYTHON_MINOR < 10) )); then
    fail "Python 3.10+ required, found $PYTHON_VERSION"
    exit 1
fi
ok "Python: $($PYTHON_CMD --version 2>&1)"

# pip check
PIP_CMD=""
for cmd in pip3 pip; do
    if command -v "$cmd" &>/dev/null; then
        PIP_CMD="$cmd"
        break
    fi
done

if [[ -z "$PIP_CMD" ]]; then
    fail "pip not found. Please install pip."
    exit 1
fi
ok "pip: $($PIP_CMD --version 2>&1 | head -1)"

# conda check (for Classiq)
HAS_CONDA=false
if command -v conda &>/dev/null; then
    HAS_CONDA=true
    ok "conda: $(conda --version 2>&1)"
else
    warn "conda not found. Classiq will be skipped."
    SKIP_CLASSIQ=true
fi

if $DRY_RUN; then
    section "Dry Run - Would Install"
    info "1. qiskit==2.3.0 qiskit-aer==0.17.2"
    info "2. pennylane==0.44.0 pennylane-lightning"
    info "3. cirq-core==1.6.1"
    info "4. pytket==2.13.0 pytket-qiskit==0.77.0"
    info "5. fastmcp (latest)"
    if ! $SKIP_CLASSIQ; then
        info "6. classiq==1.1.0 (in conda env '$CLASSIQ_CONDA_ENV' with Python 3.12)"
    fi
    exit 0
fi

# ---------------------------------------------------------------------------
# Install function with smoke test
# ---------------------------------------------------------------------------
install_package() {
    local name="$1"
    local packages="$2"
    local smoke_test="$3"

    section "Installing $name"
    info "Packages: $packages"

    if $PIP_CMD install $packages >> "$LOG_FILE" 2>&1; then
        ok "Installed $name"
    else
        fail "Failed to install $name (see $LOG_FILE)"
        return 1
    fi

    # Smoke test
    if [[ -n "$smoke_test" ]]; then
        info "Running smoke test..."
        if $PYTHON_CMD -c "$smoke_test" >> "$LOG_FILE" 2>&1; then
            ok "Smoke test passed for $name"
        else
            fail "Smoke test failed for $name"
            return 1
        fi
    fi
    return 0
}

# ---------------------------------------------------------------------------
# 1. Qiskit
# ---------------------------------------------------------------------------
install_package "IBM Qiskit" \
    "qiskit==2.3.0 qiskit-aer==0.17.2" \
    "from qiskit import QuantumCircuit; from qiskit_aer import AerSimulator; print('Qiskit OK')"

# ---------------------------------------------------------------------------
# 2. PennyLane
# ---------------------------------------------------------------------------
install_package "Xanadu PennyLane" \
    "pennylane==0.44.0 pennylane-lightning" \
    "import pennylane as qml; dev = qml.device('lightning.qubit', wires=1); print('PennyLane OK')"

# ---------------------------------------------------------------------------
# 3. Cirq
# ---------------------------------------------------------------------------
install_package "Google Cirq" \
    "cirq-core==1.6.1" \
    "import cirq; q = cirq.LineQubit(0); print('Cirq OK')"

# ---------------------------------------------------------------------------
# 4. PyTKET
# ---------------------------------------------------------------------------
install_package "Quantinuum PyTKET" \
    "pytket==2.13.0 pytket-qiskit==0.77.0" \
    "from pytket import Circuit; from pytket.extensions.qiskit import AerBackend; print('PyTKET OK')"

# ---------------------------------------------------------------------------
# 5. FastMCP
# ---------------------------------------------------------------------------
install_package "FastMCP" \
    "fastmcp" \
    "import fastmcp; print('FastMCP OK')"

# ---------------------------------------------------------------------------
# 6. Classiq (optional, conda env)
# ---------------------------------------------------------------------------
if ! $SKIP_CLASSIQ && $HAS_CONDA; then
    section "Installing Classiq (conda env)"

    if conda env list 2>/dev/null | grep -q "$CLASSIQ_CONDA_ENV"; then
        info "Conda env '$CLASSIQ_CONDA_ENV' already exists"
    else
        info "Creating conda env '$CLASSIQ_CONDA_ENV' with Python 3.12..."
        if conda create -n "$CLASSIQ_CONDA_ENV" python=3.12 -y >> "$LOG_FILE" 2>&1; then
            ok "Conda env created"
        else
            fail "Failed to create conda env (see $LOG_FILE)"
        fi
    fi

    info "Installing classiq in conda env..."
    if conda run -n "$CLASSIQ_CONDA_ENV" pip install classiq==1.1.0 >> "$LOG_FILE" 2>&1; then
        ok "Classiq installed"
    else
        warn "Classiq installation failed (non-critical)"
    fi

    info "Smoke test..."
    if conda run -n "$CLASSIQ_CONDA_ENV" python -c "import classiq; print('Classiq OK')" >> "$LOG_FILE" 2>&1; then
        ok "Classiq smoke test passed"
    else
        warn "Classiq smoke test failed (non-critical)"
    fi
fi

# ---------------------------------------------------------------------------
# Verification
# ---------------------------------------------------------------------------
section "Final Verification"

VERIFY_SCRIPT="$SCRIPT_DIR/test_all_frameworks_complete.py"
if [[ -f "$VERIFY_SCRIPT" ]]; then
    info "Running full framework verification..."
    if $PYTHON_CMD "$VERIFY_SCRIPT" 2>&1 | tee -a "$LOG_FILE"; then
        ok "All frameworks verified"
    else
        warn "Some framework tests may have failed (see output above)"
    fi
else
    info "Verifying individual imports..."
    $PYTHON_CMD -c "
import sys
results = []
for name, imp in [
    ('Qiskit', 'from qiskit import QuantumCircuit'),
    ('PennyLane', 'import pennylane'),
    ('Cirq', 'import cirq'),
    ('PyTKET', 'from pytket import Circuit'),
    ('FastMCP', 'import fastmcp'),
]:
    try:
        exec(imp)
        results.append((name, True))
    except ImportError:
        results.append((name, False))

for name, ok in results:
    status = 'OK' if ok else 'MISSING'
    print(f'  {name:12s} {status}')

if all(ok for _, ok in results):
    print('All core frameworks installed successfully!')
else:
    print('Some frameworks are missing.')
    sys.exit(1)
" 2>&1 | tee -a "$LOG_FILE"
fi

# ---------------------------------------------------------------------------
# Done
# ---------------------------------------------------------------------------
section "Installation Complete"
ok "Log saved to: $LOG_FILE"
ok "Run algorithm tests: python3 $SCRIPT_DIR/quantum_mcp_server/test_top20_algorithms.py"
ok "Start MCP server:   python3 $SCRIPT_DIR/quantum_mcp_server/server.py"
echo ""
