from fastmcp import FastMCP
from typing import List, Dict, Any

mcp = FastMCP("Type Test")

# Test 1: List[Dict[str, Any]]
@mcp.tool()
def test_complex_type(gates: List[Dict[str, Any]]) -> dict:
    """Test complex type."""
    return {"gates_count": len(gates)}

# Test 2: Just list
@mcp.tool()
def test_simple_list(gates: list) -> dict:
    """Test simple list."""
    return {"gates_count": len(gates)}

if __name__ == "__main__":
    mcp.run()
