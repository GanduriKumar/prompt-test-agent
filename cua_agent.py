import asyncio
import logging
import json
from typing import Dict, List
from urllib.parse import urlparse

from cua_tools import generate_functional_tests, generate_nfr_tests

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    force=True
)


def validate_test_structure(tests: Dict[str, List[Dict]]) -> bool:
    """
    Validates the structure of a test suite.
    This function checks if the provided `tests` dictionary contains the required 
    keys for functional and non-functional tests. It also verifies that each test 
    within these categories has the necessary attributes.
    Args:
        tests (Dict[str, List[Dict]]): A dictionary containing two keys:
            - "functional_tests": A list of dictionaries representing functional tests.
            - "nfr_tests": A list of dictionaries representing non-functional tests.
    Returns:
        bool: Returns True if the structure is valid and all required keys are present,
              otherwise returns False. Logs warnings for any missing keys in the tests.
    """
    
    try:
        # Check top-level structure
        if not isinstance(tests, dict):
            logging.error("Tests is not a dictionary")
            return False
        
        if "functional_tests" not in tests or "nfr_tests" not in tests:
            logging.error("Missing required keys: functional_tests or nfr_tests")
            return False
        
        # Validate functional tests
        for i, test in enumerate(tests.get("functional_tests", [])):
            required_keys = ["id", "title", "steps", "expected_result"]
            missing = [k for k in required_keys if k not in test]
            if missing:
                logging.warning(f"Functional test {i} missing keys: {missing}")
        
        # Validate NFR tests
        for i, test in enumerate(tests.get("nfr_tests", [])):
            required_keys = ["id", "category", "title", "acceptance_criteria"]
            missing = [k for k in required_keys if k not in test]
            if missing:
                logging.warning(f"NFR test {i} missing keys: {missing}")
        
        return True
        
    except Exception as e:
        logging.error(f"Validation error: {e}")
        return False


async def generate_all_tests(url: str, business_context: str) -> Dict[str, List[Dict]]:
    """
    Asynchronously generates both functional and non-functional requirement (NFR) tests for a given URL.
    This function runs two test generation tasks concurrently: one for functional tests and another for NFR tests.
    It handles potential exceptions during the test generation process and ensures that the returned results are 
    in the form of lists, even in the case of errors.
    Args:
    url (str): The URL for which tests are to be generated.
    business_context (str): The business context that may influence test generation.
    Returns:
    Dict[str, List[Dict]]: A dictionary containing two keys:
        - "functional_tests": A list of generated functional tests.
        - "nfr_tests": A list of generated non-functional requirement tests.
    Logs:
    - Information about the start of the test generation process.
    - Errors encountered during the generation of functional or NFR tests.
    - The number of tests generated for both functional and NFR categories.
    """
    logging.info(f"Starting test generation for URL: {url}")
    
    # Pre-validate that we can access the URL
    try:
        from cua_tools import get_interactive_elements
        logging.info("Testing page accessibility...")
        elements = await get_interactive_elements(url)
        
        if not elements or len(elements) == 0:
            logging.warning(f"No interactive elements found on {url}")
            logging.warning("This may indicate:")
            logging.warning("  1. Page requires JavaScript (loaded but not executed)")
            logging.warning("  2. Page has no forms/buttons/links")
            logging.warning("  3. Page uses shadow DOM or iframes")
            logging.info("Proceeding with test generation anyway...")
        else:
            logging.info(f"Found {len(elements)} interactive elements")
            
    except Exception as e:
        logging.error(f"Failed to access page: {e}")
        logging.error("Cannot generate tests without accessing the page.")
        return {
            "functional_tests": [],
            "nfr_tests": []
        }
    
    # Run both test generation tasks concurrently
    func_tests_task = generate_functional_tests(url, business_context)
    nfr_tests_task = generate_nfr_tests(url, business_context)
    
    functional_tests, nfr_tests = await asyncio.gather(
        func_tests_task,
        nfr_tests_task,
        return_exceptions=True
    )
    
    # Handle potential errors
    if isinstance(functional_tests, Exception):
        logging.error(f"Functional test generation failed: {functional_tests}")
        functional_tests = []
    
    if isinstance(nfr_tests, Exception):
        logging.error(f"NFR test generation failed: {nfr_tests}")
        nfr_tests = []
    
    # Ensure we have lists
    if not isinstance(functional_tests, list):
        functional_tests = []
    if not isinstance(nfr_tests, list):
        nfr_tests = []
    
    logging.info(f"Generated {len(functional_tests)} functional tests")
    logging.info(f"Generated {len(nfr_tests)} NFR tests")
    
    return {
        "functional_tests": functional_tests,
        "nfr_tests": nfr_tests
    }


def normalize_url(url: str) -> str:
    """
    Normalize and fix common URL issues.
    
    Args:
        url: User-provided URL
    
    Returns:
        Normalized URL with proper protocol
    """
    url = url.strip()
    
    # Remove trailing slashes
    url = url.rstrip('/')
    
    # Add protocol if missing
    if not url.startswith(('http://', 'https://')):
        url = f"https://{url}"
    
    # Force HTTPS for known sites that require it
    known_https_sites = [
        'google.com',
        'facebook.com',
        'twitter.com',
        'github.com',
        'linkedin.com',
        'microsoft.com'
    ]
    
    if url.startswith('http://'):
        for site in known_https_sites:
            if site in url:
                url = url.replace('http://', 'https://', 1)
                logging.info(f"Forcing HTTPS for {site}: {url}")
                break
    
    return url


def main():
    """
    Main function to generate tests for a given URL.
    This function prompts the user for a URL, validates the input, and generates 
    functional and non-functional tests based on the provided URL. It also handles 
    the addition of the 'https://' prefix if the URL does not start with 'http://' 
    or 'https://'. The generated tests are validated for structure and saved to 
    a JSON file. Logging is used to provide feedback on the process, including 
    error handling for empty URLs and file writing issues.
    Steps:
    1. Prompt the user for a URL and strip any leading/trailing whitespace.
    2. Validate the URL to ensure it is not empty and starts with 'http://' or 'https://'.
    3. Generate tests asynchronously using the provided URL and a predefined business context.
    4. Validate the structure of the generated tests and log any warnings.
    5. Count the total number of generated tests and log appropriate messages.
    6. Write the generated tests to a JSON file, handling any potential IO errors.
    Returns:
        None
    """
    url = input("Enter the URL to open: ").strip()
    
    if not url:
        logging.error("URL cannot be empty")
        return
    
    # Normalize URL
    url = normalize_url(url)
    logging.info(f"Using URL: {url}")
    
    business_context = "Web application under test"
    
    # Generate tests
    try:
        all_tests = asyncio.run(generate_all_tests(url, business_context))
    except KeyboardInterrupt:
        logging.info("Test generation cancelled by user")
        return
    except Exception as e:
        logging.error(f"Test generation failed with error: {e}")
        logging.error("Common issues:")
        logging.error("  1. URL is not accessible (firewall, VPN, etc.)")
        logging.error("  2. Site requires authentication")
        logging.error("  3. Site blocks automated browsers")
        logging.error("  4. LLM API key is invalid or quota exceeded")
        return
    
    # Validate structure
    if not validate_test_structure(all_tests):
        logging.warning("Generated tests have validation warnings (see above)")
    
    # Check if we have any tests
    total_tests = len(all_tests['functional_tests']) + len(all_tests['nfr_tests'])
    if total_tests == 0:
        logging.error("No tests were generated. Check logs for errors.")
        logging.info("Troubleshooting steps:")
        logging.info("  1. Verify the URL is accessible in a browser")
        logging.info("  2. Try using full HTTPS URL (e.g., https://www.google.com)")
        logging.info("  3. Check your LLM provider API key and quota")
        logging.info("  4. Enable debug logging: logging.basicConfig(level=logging.DEBUG)")
        logging.info("Saving empty test file as placeholder")
    
    # Write to JSON file
    output_file = "generated_tests.json"
    try:
        with open(output_file, "w", encoding='utf-8') as f:
            json.dump(all_tests, f, indent=2, ensure_ascii=False)
        
        logging.info(f"Tests saved to: {output_file}")
        logging.info(f"Total tests generated: {total_tests}")
        
        if total_tests > 0:
            logging.info("✅ Test generation completed successfully")
        else:
            logging.warning("⚠️  No tests generated - check AI model and prompts")
            
    except IOError as e:
        logging.error(f"Failed to write output file: {e}")


if __name__ == "__main__":
    main()