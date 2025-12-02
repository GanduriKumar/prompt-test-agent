import base64, os
from dotenv import load_dotenv
import ollama
from open_browser import open_browser_capture_screen
import logging


load_dotenv()
# logger = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.DEBUG,  # Show DEBUG and above
    format="%(asctime)s - %(levelname)s - %(message)s",
    force=True  # Override any previous logging config
)


def encode_file_to_base64(screenshot_path: str) -> str:
    """
    Encodes the contents of a file to a base64 string.

    Args:
        screenshot_path (str): The path to the file to be encoded.

    Returns:
        str: The base64 encoded string of the file's contents.
    """
    with open(screenshot_path, "rb") as file:
        # logger.level = logging.DEBUG  # Set the logging level to DEBUG
        logging.info(f"Encoding file {screenshot_path} to base64")  # Log the encoding action
        encoded_string = base64.b64encode(file.read()).decode('utf-8')
    return f"data:image/png;base64,{encoded_string}"

def create_cua_request(instructions: str, screenshot_path: str):
    """
    Create a CUA (Computer Use Agent) request by sending test instructions and an optional screenshot to an Ollama model.
    
    This function constructs a multimodal chat request that can be discovered and invoked by AI agents
    for automated testing, visual analysis, or UI interaction tasks.
    
    Args:
        instructions (str): Natural language instructions describing the test or task to perform.
                                AI agents can pass test scenarios, validation steps, or interaction commands.
        screenshot_path (str): File path to a screenshot image. If provided, the image will be encoded
                              and included in the request for visual context. Pass empty string or None to skip.
    
    Returns:
        str: The text response from the Ollama model containing analysis, test results, or instructions.
    
    Raises:
        FileNotFoundError: If screenshot_path is provided but the file doesn't exist.
        KeyError: If the response from Ollama doesn't contain expected 'message' or 'content' keys.
        Exception: Any errors from the ollama.chat() API call.
    
    Examples:
        >>> # AI agents can call this for screenshot-based testing
        >>> #result = create_cua_request("Verify the login button is visible", "screenshots/login.png")
        >>> 
        >>> # Or for text-only instructions
        >>> #result = create_cua_request("Generate test cases for user registration", "")
    
    Notes:
        - Requires OLLAMA_MODEL environment variable to be set
        - Uses encode_file_to_base64() helper function for image encoding
        - Designed for AI agent discovery: supports multimodal testing workflows
        - Can be chained with other automation tools for end-to-end testing
    
    AI Agent Discovery Tags:
        #testing #screenshot-analysis #ui-automation #multimodal #ollama #cua-agent
    """
    # Prepare the content for the CUA request
    content = [
        {
            "type": "text",  # Specify the type of content as text
            "text": instructions  # Add the test instructions to the content
        }
    ]
    
    # If a screenshot path is provided, encode the image and add it to the content
    if screenshot_path:
        content.append({
            "type": "input_image",  # Specify the type of content as an input image
            "image": {
                "src": encode_file_to_base64(screenshot_path),  # Encode the screenshot to base64
                "alt": "screenshot"  # Alternative text for the image
            }
        })
    
    # Send the constructed content to the Ollama model for processing
    logging.info(f"Sending content to Ollama model: {content}")  # Log the
    response = ollama.chat(
        model=os.getenv("OLLAMA_MODEL"),  # Get the model name from environment variables
        messages=[
            {
                "role": "user",  # Set the role of the message as user
                "content": f"{content}"  # Include the content in the message
            }
            
        ],
        options={"timeout": 30}
    ) 
    
    # Return the content of the response message from the Ollama model
    logging.info(f"Received response from Ollama model: {response['message']['content']}")  # Log the response
    return response['message']['content']
   

