#!/usr/bin/env python3
"""Test Classiq installation - basic import test"""
print("Testing Classiq installation...")

try:
    import classiq
    from classiq import qfunc, QArray, QBit, Output, H, CX, allocate, create_model
    
    print(f"✓ Classiq {classiq.__version__} successfully installed!")
    print(f"  Package location: {classiq.__file__}")
    print(f"  Core imports working")
    
    # Test creating a model definition (doesn't require cloud)
    @qfunc
    def bell_state(res: Output[QArray[QBit]]):
        allocate(2, res)
        H(res[0])
        CX(res[0], res[1])
    
    print(f"  Function decorators working")
    print(f"\n✓ Classiq is ready for use!")
    print(f"  Note: Circuit synthesis requires authentication with Classiq cloud")
    
except ImportError as e:
    print(f"✗ Failed to import Classiq: {e}")
    exit(1)
except Exception as e:
    print(f"✗ Unexpected error: {e}")
    exit(1)
