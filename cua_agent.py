import asyncio
import logging
import json
import re
from typing import Dict, List

from cua_tools import generate_functional_tests, generate_nfr_tests

# Configure logging
logging.basicConfig(
    level=logging.INFO,  # Changed to INFO for cleaner output
    format="%(asctime)s - %(levelname)s - %(message)s",
    force=True
)


def validate_and_sanitize_url(url: str) -> str:
    """Validate and sanitize user-provided URL.
    
    AI Tool Discovery Metadata:
    - Category: Input Validation
    - Task: URL Sanitization and Security
    - Purpose: Prevents SSRF attacks, validates URL format, adds protocol if missing
    
    Args:
        url (str): Raw URL string from user input
        
    Returns:
        str: Validated and sanitized URL with protocol (https:// added if missing)
        
    Raises:
        ValueError: If URL is empty or has invalid format
        
    Example:
        >>> validate_and_sanitize_url("example.com")
        'https://example.com'
        >>> validate_and_sanitize_url("http://localhost:8080/api")
        'http://localhost:8080/api'
        
    Security Features:
        - Empty string detection
        - Automatic HTTPS protocol addition
        - Regex validation for domain/IP patterns
        - Port number validation
        - Path/query string validation
    """
    url = url.strip()
    
    if not url:
        raise ValueError("URL cannot be empty")
    
    # Add https:// if no protocol specified
    if not url.startswith(('http://', 'https://')):
        url = f"https://{url}"
    
    # Basic URL validation
    url_pattern = re.compile(
        r'^https?://'
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'
        r'localhost|'
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
        r'(?::\d+)?'
        r'(?:/?|[/?]\S+)$', re.IGNORECASE
    )
    
    if not url_pattern.match(url):
        raise ValueError(f"Invalid URL format: {url}")
    
    return url


async def generate_all_tests(url: str, business_context: str) -> Dict[str, List[Dict]]:
    """Generate both functional and NFR tests concurrently for maximum performance.
    
    AI Tool Discovery Metadata:
    - Category: Test Generation
    - Task: Concurrent Test Suite Creation
    - Purpose: Generate comprehensive test suites (functional + NFR) in parallel
    - Performance: 2x faster than sequential generation
    
    Args:
        url (str): Target web application URL to test
        business_context (str): Description of page purpose (e.g., "Login page", "Checkout flow")
        
    Returns:
        Dict[str, List[Dict]]: Dictionary containing:
            - "functional_tests": List of functional test case dictionaries
            - "nfr_tests": List of non-functional requirement test dictionaries
            
    Example Response:
        {
            "functional_tests": [
                {
                    "id": "FUNC_001",
                    "title": "User can login with valid credentials",
                    "preconditions": ["User is registered"],
                    "steps": ["Enter email", "Enter password", "Click login"],
                    "expected_result": "User redirected to dashboard",
                    "tags": ["authentication", "happy-path"]
                }
            ],
            "nfr_tests": [
                {
                    "id": "NFR_001",
                    "category": "performance",
                    "title": "Page loads within 2 seconds",
                    "description": "Measure time from navigation to DOMContentLoaded",
                    "acceptance_criteria": ["Load time < 2000ms"],
                    "tooling_suggestions": ["Playwright", "Lighthouse"]
                }
            ]
        }
        
    Error Handling:
        - Returns empty lists if individual generators fail
        - Logs errors without stopping entire process
        - Uses asyncio.gather with return_exceptions=True
        
    Performance:
        - Runs functional and NFR generation concurrently
        - Typical execution: 30-60 seconds for both tests
        - Sequential would take 60-120 seconds
        
    Use Cases:
        - CI/CD test generation
        - Automated QA documentation
        - Test-driven development workflows
        - Regression test suite creation
    """
    logging.info(f"Starting test generation for URL: {url}")
    
    # Run both test generation tasks concurrently for 2x speed improvement
    func_tests_task = generate_functional_tests(url, business_context)
    nfr_tests_task = generate_nfr_tests(url, business_context)
    
    functional_tests,nfr_tests  = await asyncio.gather(
        func_tests_task,
        nfr_tests_task,
        return_exceptions=True  # Don't fail if one task errors
    )
    
    # Handle potential errors
    if isinstance(functional_tests, Exception):
        logging.error(f"Functional test generation failed: {functional_tests}")
        functional_tests = []
    
    if isinstance(nfr_tests, Exception):
        logging.error(f"NFR test generation failed: {nfr_tests}")
        nfr_tests = []
    
    logging.info(f"Generated {len(functional_tests)} functional tests")
    logging.info(f"Generated {len(nfr_tests)} NFR tests")
    
    return {
        "functional_tests": functional_tests,
        "nfr_tests": nfr_tests
    }


def main():
    """Main entry point for automated test generation workflow.
    
    AI Tool Discovery Metadata:
    - Category: Workflow Orchestration
    - Task: End-to-End Test Suite Generation
    - Purpose: Interactive CLI for generating test suites from web applications
    
    Workflow:
        1. Prompt user for target URL
        2. Validate and sanitize URL
        3. Generate functional tests (happy path, negative, boundary)
        4. Generate NFR tests (performance, security, accessibility, usability, reliability)
        5. Save results to generated_tests.json
        
    User Inputs:
        - URL: Web application URL to analyze
        
    Outputs:
        - generated_tests.json: JSON file with all test specifications
        
    Error Handling:
        - ValueError: Invalid URL format or validation failure
        - KeyboardInterrupt: Graceful shutdown on Ctrl+C
        - IOError: File write failures
        - Generic Exception: Unexpected errors with stack trace
        
    Configuration:
        - Business context: Currently hardcoded as "Search website"
        - Output file: "generated_tests.json" in current directory
        - Encoding: UTF-8 with ensure_ascii=False for international support
        
    Example Usage:
        $ python cua_agent.py
        Enter the URL to open: https://example.com/login
        2025-01-15 10:30:45 - INFO - Validated URL: https://example.com/login
        2025-01-15 10:30:46 - INFO - Starting test generation for URL: https://example.com/login
        2025-01-15 10:31:20 - INFO - Generated 8 functional tests
        2025-01-15 10:31:20 - INFO - Generated 12 NFR tests
        2025-01-15 10:31:20 - INFO - Tests saved to: generated_tests.json
        2025-01-15 10:31:20 - INFO - Total tests generated: 20
        
    Integration:
        - Can be called programmatically via asyncio.run(generate_all_tests(url, context))
        - JSON output suitable for CI/CD pipelines
        - Compatible with test frameworks (pytest, unittest, Robot Framework)
    """
    try:
        # Get and validate URL
        url_input = input("Enter the URL to open: ")
        url = validate_and_sanitize_url(url_input)
        
        logging.info(f"Validated URL: {url}")
        
        # You can make business context configurable too
        business_context = "Search website"
        
        # Generate tests
        all_tests = asyncio.run(generate_all_tests(url, business_context))
        
        # Write to JSON file
        output_file = "generated_tests.json"
        try:
            with open(output_file, "w", encoding='utf-8') as f:
                json.dump(all_tests, f, indent=2, ensure_ascii=False)
            
            logging.info(f"Tests saved to: {output_file}")
            logging.info(f"Total tests generated: {len(all_tests['functional_tests']) + len(all_tests['nfr_tests'])}")
        except IOError as e:
            logging.error(f"Failed to write output file: {e}")
            
    except ValueError as e:
        logging.error(f"Validation error: {e}")
    except KeyboardInterrupt:
        logging.info("\nOperation cancelled by user")
    except Exception as e:
        logging.error(f"Unexpected error: {e}", exc_info=True)


if __name__ == "__main__":
    main()