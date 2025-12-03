import logging, asyncio
from cua_tools import encode_file_to_base64, extract_elements_from_image, open_browser_capture_screen, generate_automation_code, execute_automation_code

async def main():
    # Configure logging to display debug messages with timestamps
    logging.basicConfig(
        level=logging.DEBUG,  # Show DEBUG and above
        format="%(asctime)s - %(levelname)s - %(message)s",
        force=True  # Override any previous logging config
    )

    # USER INPUT: Prompt the user to enter a target URL for web page analysis
    url = input("Enter the URL to open: ")
    logging.debug(f"Opening URL: {url}")  # Log the URL being opened

    # SCREENSHOT CAPTURE: Open the specified URL in a browser and capture a screenshot
    # The screenshot will be saved as "screenshot.png" in the current directory
    await open_browser_capture_screen(url, "screenshot.png")
    logging.debug(f"Screenshot saved as screenshot.png")  # Log the action of saving the screenshot

    # Encode the captured screenshot image to base64 format for processing
    encoded_image = encode_file_to_base64("screenshot.png")
    
    # Extract elements from the encoded image, returning a dictionary of elements
    elements_dict = extract_elements_from_image(encoded_image)
    logging.debug(f"Extracted Elements: {elements_dict}")  # Log the extracted elements

    # Generate automation code based on the extracted elements
    action_code = generate_automation_code(elements_dict,url)
    logging.debug(f"Generated Automation Code: {action_code}")  # Log the generated automation code

    # Execute the generated automation code on the specified URL
    await execute_automation_code(action_code, url)

if __name__ == "__main__":
    # Run the main function in an asyncio event loop
    asyncio.run(main())

