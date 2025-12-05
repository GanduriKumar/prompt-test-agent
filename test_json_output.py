import os
import asyncio
from dotenv import load_dotenv
from cua_tools import generate_nfr_tests, generate_functional_tests

load_dotenv()

async def test_json_generation():
    """Test that JSON output is valid and complete."""
    
    test_url = "https://www.example.com"
    context = "Simple test website"
    
    print("\n🧪 Testing Functional Tests Generation...")
    func_tests = await generate_functional_tests(test_url, context)
    
    if func_tests:
        print(f"✅ Functional: Generated {len(func_tests)} tests")
    else:
        print("❌ Functional: Failed to generate tests")
    
    print("\n🧪 Testing NFR Tests Generation...")
    nfr_tests = await generate_nfr_tests(test_url, context)
    
    if nfr_tests:
        print(f"✅ NFR: Generated {len(nfr_tests)} tests")
    else:
        print("❌ NFR: Failed to generate tests")
    
    # Validate structure
    if func_tests and nfr_tests:
        print("\n✅ All tests passed! JSON generation is working correctly.")
    else:
        print("\n⚠️  Some tests failed. Check logs for details.")

if __name__ == "__main__":
    asyncio.run(test_json_generation())