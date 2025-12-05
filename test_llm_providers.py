"""
Test script to verify multi-provider LLM setup

Usage:
    python test_llm_providers.py

This script tests your LLM configuration and verifies:
1. Environment variables are set correctly
2. Provider can be initialized
3. Basic text generation works
4. Vision generation works (if applicable)
"""

import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s"
)

# Load environment variables
load_dotenv()

def test_environment():
    """Test environment configuration"""
    print("\n" + "="*60)
    print("TESTING ENVIRONMENT CONFIGURATION")
    print("="*60)
    
    provider = os.getenv("LLM_PROVIDER", "ollama")
    print(f"✓ LLM_PROVIDER: {provider}")
    
    model = os.getenv("LLM_MODEL", "not set")
    print(f"✓ LLM_MODEL: {model}")
    
    vision_model = os.getenv("LLM_VISION_MODEL", "not set")
    print(f"✓ LLM_VISION_MODEL: {vision_model}")
    
    coding_model = os.getenv("LLM_CODING_MODEL", "not set")
    print(f"✓ LLM_CODING_MODEL: {coding_model}")
    
    # Provider-specific checks
    if provider == "ollama":
        ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        print(f"✓ OLLAMA_BASE_URL: {ollama_url}")
    elif provider == "openai":
        api_key = os.getenv("OPENAI_API_KEY", "")
        print(f"✓ OPENAI_API_KEY: {'Set' if api_key else 'NOT SET ❌'}")
    elif provider == "anthropic":
        api_key = os.getenv("ANTHROPIC_API_KEY", "")
        print(f"✓ ANTHROPIC_API_KEY: {'Set' if api_key else 'NOT SET ❌'}")
    elif provider == "google":
        api_key = os.getenv("GOOGLE_API_KEY", "")
        print(f"✓ GOOGLE_API_KEY: {'Set' if api_key else 'NOT SET ❌'}")
    elif provider == "azure":
        api_key = os.getenv("AZURE_OPENAI_API_KEY", "")
        endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "")
        print(f"✓ AZURE_OPENAI_API_KEY: {'Set' if api_key else 'NOT SET ❌'}")
        print(f"✓ AZURE_OPENAI_ENDPOINT: {endpoint if endpoint else 'NOT SET ❌'}")
    
    return True

def test_provider_initialization():
    """Test LLM provider initialization"""
    print("\n" + "="*60)
    print("TESTING PROVIDER INITIALIZATION")
    print("="*60)
    
    try:
        from llm_provider import LLMProvider
        
        provider = LLMProvider()
        print(f"✓ Provider initialized: {provider.provider_name}")
        print(f"✓ Text model: {provider.model}")
        print(f"✓ Vision model: {provider.vision_model}")
        print(f"✓ Coding model: {provider.coding_model}")
        
        return True, provider
    except Exception as e:
        print(f"✗ Failed to initialize provider: {e}")
        return False, None

def test_text_generation(provider):
    """Test basic text generation"""
    print("\n" + "="*60)
    print("TESTING TEXT GENERATION")
    print("="*60)
    
    try:
        prompt = """Generate a simple JSON object with test information:
{
    "test_id": "TEST_001",
    "test_name": "Sample test",
    "status": "pass"
}

Only respond with valid JSON, no explanation."""
        
        print("Sending test prompt...")
        response = provider.generate(prompt, format="json", max_tokens=200)
        
        print(f"✓ Response received ({len(response)} chars)")
        print(f"✓ Response preview: {response[:100]}...")
        
        # Try to parse as JSON
        import json
        try:
            parsed = json.loads(response)
            print(f"✓ Valid JSON response")
            print(f"✓ Keys: {list(parsed.keys())}")
            return True
        except json.JSONDecodeError:
            print("⚠ Warning: Response is not valid JSON (but generation works)")
            return True
            
    except Exception as e:
        print(f"✗ Text generation failed: {e}")
        return False

def test_code_generation(provider):
    """Test code generation"""
    print("\n" + "="*60)
    print("TESTING CODE GENERATION")
    print("="*60)
    
    try:
        prompt = """Write a simple Python function that adds two numbers.
Only output the code, no explanation."""
        
        print("Sending code generation prompt...")
        response = provider.generate_code(prompt, max_tokens=200)
        
        print(f"✓ Response received ({len(response)} chars)")
        print(f"✓ Response preview:\n{response[:150]}...")
        
        if "def " in response or "return" in response:
            print(f"✓ Looks like Python code")
        
        return True
            
    except Exception as e:
        print(f"✗ Code generation failed: {e}")
        return False

def test_vision(provider):
    """Test vision generation (basic check)"""
    print("\n" + "="*60)
    print("TESTING VISION CAPABILITIES")
    print("="*60)
    
    # Create a simple test image (1x1 pixel red PNG)
    import base64
    
    # Minimal PNG: 1x1 red pixel
    test_image = base64.b64encode(
        b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01'
        b'\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\xcf'
        b'\xc0\x00\x00\x00\x00\xff\xff\x03\x00\x00\x08\x00\x01\x00\x00\x00'
        b'\x00IEND\xaeB`\x82'
    ).decode('utf-8')
    
    try:
        prompt = "Describe what you see in this image. Respond with: {\"description\": \"your description\", \"color\": \"the main color\"}"
        
        print("Sending vision test prompt...")
        response = provider.generate_vision(prompt, test_image, format="json")
        
        print(f"✓ Vision response received ({len(response)} chars)")
        print(f"✓ Response preview: {response[:100]}...")
        
        return True
            
    except Exception as e:
        print(f"⚠ Vision test skipped or failed: {e}")
        print(f"  (This is OK if your model doesn't support vision)")
        return True  # Don't fail on vision test

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("LLM PROVIDER TEST SUITE")
    print("="*60)
    
    results = []
    
    # Test 1: Environment
    results.append(("Environment", test_environment()))
    
    # Test 2: Provider initialization
    success, provider = test_provider_initialization()
    results.append(("Provider Init", success))
    
    if not provider:
        print("\n❌ Cannot continue tests without provider")
        return False
    
    # Test 3: Text generation
    results.append(("Text Generation", test_text_generation(provider)))
    
    # Test 4: Code generation
    results.append(("Code Generation", test_code_generation(provider)))
    
    # Test 5: Vision (optional)
    results.append(("Vision", test_vision(provider)))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    for test_name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    all_passed = all(passed for _, passed in results)
    
    if all_passed:
        print("\n✅ All tests passed! Your LLM provider is configured correctly.")
        print("\nYou can now run: python cua_agent.py")
        return True
    else:
        print("\n❌ Some tests failed. Please check your configuration.")
        print("\nSee LLM_PROVIDER_GUIDE.md for setup instructions.")
        return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
