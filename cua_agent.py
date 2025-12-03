import logging
from cua_tools import encode_file_to_base64, extract_elements_from_image,open_browser_capture_screen



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


encoded_image = encode_file_to_base64("screenshot.png")
elements_dict = extract_elements_from_image(encoded_image)

logging.info(f"Extracted Elements: {elements_dict}")    




