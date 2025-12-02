from cua_client import create_cua_request
from open_browser import open_browser_capture_screen

import logging, os
from dotenv import load_dotenv

# Load environment variables from .env file for configuration management
load_dotenv()
# logger = logging.getLogger(__name__)

# Configure logging system for debugging and monitoring
# Purpose: Track application flow and troubleshoot issues
logging.basicConfig(
    level=logging.DEBUG,  # Show DEBUG and above
    format="%(asctime)s - %(levelname)s - %(message)s",
    force=True  # Override any previous logging config
)

# USER INPUT: Collect target URL from user for web page analysis
# This URL will be opened in a browser for screenshot capture
url = input("Enter the URL to open: ")
logging.info(f"Opening URL: {url}")  # Log the URL being opened

# SCREENSHOT CAPTURE: Open the specified URL in a browser and capture a screenshot
# Output: Saves screenshot as "screenshot.png" in the current directory
# Dependencies: Requires open_browser_capture_screen function from open_browser module
open_browser_capture_screen(url, "screenshot.png")
logging.info(f"Screenshot saved as screenshot.png")  # Log the screenshot saving action

# FILE CONFIGURATION: Set paths and instructions for CUA (Computer Use Agent) request
file_path = "screenshot.png"  # Path to the screenshot file
# ANALYSIS TASK: Define instructions for analyzing the captured webpage screenshot
# Task: Extract and list all HTML input tags present in the webpage
test_instructions = "List all the HTML inouts tags in the webpage"  # Instructions for the CUA request

# FILE VALIDATION: Verify screenshot file exists before processing
# Prevents errors from attempting to process non-existent files
if os.path.exists(file_path):
    logging.info(f"File {file_path} exists. Proceeding with CUA request.")  # Log file existence
    
    # CUA REQUEST: Send screenshot and instructions to CUA service for analysis
    # Input: Analysis instructions and screenshot file path
    # Output: Returns analysis results from CUA service
    result = create_cua_request(instructions=test_instructions, screenshot_path=file_path)
    logging.info(f"CUA Request Result: {result}")  # Log the result of the CUA request
else:
    # ERROR HANDLING: Log error when screenshot file is missing
    # Indicates failure in screenshot capture or incorrect file path
    logging.error(f"File {file_path} does not exist.")