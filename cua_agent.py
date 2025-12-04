import asyncio, logging, json
from playwright.async_api import async_playwright

from cua_tools import get_interactive_elements, build_nfr_tests_prompt, build_functional_tests_prompt, generate_functional_tests, generate_final_output, generate_nfr_tests

# Configure logging to display debug-level messages with timestamps
logging.basicConfig(
    level=logging.DEBUG,  # Show DEBUG and above
    format="%(asctime)s - %(levelname)s - %(message)s",
    force=True  # Override any previous logging config
)

# Prompt user for the target URL to analyze
url = input("Enter the URL to open: ")
logging.debug(f"Opening URL: {url}")

# Generate functional test cases based on the provided URL and business context
# Uses async execution to interact with the web page and extract testable elements
functional_tests = asyncio.run(generate_functional_tests(url=url, business_context="Search website"))
logging.info(f"Generated Functional Tests: {functional_tests}")

# Generate non-functional requirement (NFR) tests such as performance, accessibility, etc.
# Also uses async execution for web page analysis
nfr_tests = asyncio.run(generate_nfr_tests(url=url, business_context="Search website"))
logging.info(f"Generated NFR Tests: {nfr_tests}")

# Combine both test types into a single dictionary structure
all_tests = {
    "functional_tests": functional_tests,
    "nfr_tests": nfr_tests
}

# Write the generated tests to a JSON file for later use or review
with open("generated_tests.json", "w") as f:
    json.dump(all_tests, f, indent=2)