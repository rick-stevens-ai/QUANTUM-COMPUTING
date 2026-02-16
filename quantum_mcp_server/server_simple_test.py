"""Simple test of FastMCP server"""
from fastmcp import FastMCP

mcp = FastMCP("Quantum Test")

@mcp.tool()
def test_simple() -> dict:
    """Simple test with no parameters."""
    return {"status": "working", "value": 42}

@mcp.tool()
def test_with_param(value: int) -> dict:
    """Test with a simple parameter."""
    return {"input": value, "output": value * 2}

if __name__ == "__main__":
    print("Starting simple test server...")
    mcp.run()
