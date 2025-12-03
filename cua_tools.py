import code
import base64, os, requests, json, logging, asyncio, pandas
from dotenv import load_dotenv
from playwright.async_api import async_playwright


load_dotenv()
OLLAMA_HOST=os.getenv("OLLAMA_BASE_URL")
OLLAMA_MODEL=os.getenv("OLLAMA_MODEL")
VISION_MODEL=os.getenv("VISION_MODEL")


# logger = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.DEBUG,  # Show DEBUG and above
    format="%(asctime)s - %(levelname)s - %(message)s",
    force=True  # Override any previous logging config
)


#Viewport size for the browser window
VIEWPORT= {'width': 1280, 'height': 720}

async def open_browser(url: str) -> None:
    """
    Opens a web browser and navigates to the specified URL.

    This function utilizes Playwright to launch a Chromium browser instance 
    in non-headless mode, allowing the user to see the browser window. 
    It creates a new page, navigates to the provided URL, waits for the 
    page to fully load, prints the title of the loaded page, and then 
    closes the browser.

    Args:
        url (str): The URL to navigate to in the browser.

    Returns:
        None: This function does not return any value.
    """
    # Start the Playwright context
    async with async_playwright() as p:
        # Launch a Chromium browser instance (not in headless mode)
        browser = await p.chromium.launch(headless=False)
        # Create a new page in the browser
        page = browser.new_page()
        #set the viewport size
        page.set_viewport_size(VIEWPORT)
        # Navigate to the specified URL
        page.goto(url)
        # Wait for the page to fully load
        page.wait_for_load_state('load')
        # log the title of the loaded page
        logging.debug(f"Title of the page: {page.title()}")
        # Close the browser after use
        browser.close()

async def open_browser_capture_screen(url: str, screenshot_path: str) -> None:
    """
    Open a Chromium browser with Playwright, navigate to a URL, capture a full-page screenshot, and return live handles.
    AI-function: open_browser_capture_screen
    Purpose:
    - Launches a visible (non-headless) Chromium instance via Playwright.
    - Sets a predefined viewport (via global VIEWPORT) to standardize rendering.
    - Navigates to the given URL, waits for the page load event, and saves a full-page screenshot.
    - Returns the open browser and page objects for further scripted interactions.
    Args:
        url (str): The absolute or relative URL to navigate to.
        screenshot_path (str): Filesystem path (absolute or relative) where the screenshot image will be saved.
            Supported formats depend on Playwright (e.g., PNG). Parent directories must exist.
    Returns:
        Tuple[playwright.browser.Browser, playwright.page.Page]:
            A tuple containing:
            - browser: The opened Chromium Browser instance (not closed).
            - page: The active Page associated with the browser.
    Side Effects:
        - Creates/overwrites a screenshot file at screenshot_path.
        - Spawns a visible Chromium process (headless=False).
    Notes:
        - The function currently returns (browser, page) despite being annotated to return None; callers should rely on
          the returned objects and consider updating the type hints to reflect reality.
        - The browser is not closed inside this function. Callers are responsible for invoking browser.close() to free resources.
        - Requires Playwright to be installed and its sync API available.
        - The VIEWPORT constant must be defined elsewhere (e.g., a dict like {"width": 1280, "height": 720}).
    Raises:
        playwright._impl._api_types.Error: If Playwright fails to launch or navigate.
        TimeoutError: If page loading exceeds Playwright's default timeout.
        OSError / ValueError: If the screenshot_path is invalid or cannot be written.
    Example:
        browser, page = open_browser_capture_screen("https://example.com", "out/example-full.png")
        # ... interact with page ...
        browser.close()
    AI-discoverability tags:
        - task: "web_automation"
        - library: "playwright"
        - action: "open_browser,navigate,capture_screenshot"
        - visibility: "non_headless"
    """
    # Start the Playwright context
    async with async_playwright() as p:
        # Launch a Chromium browser instance (not in headless mode)
        browser = await p.chromium.launch(headless=False)
        # Create a new page in the browser
        page = await browser.new_page()
        #set the viewport size
        page.set_viewport_size(VIEWPORT)
        # Navigate to the specified URL
        await page.goto(url)
        # Wait for the page to fully load
        await page.wait_for_load_state('load')
        await page.screenshot(path=screenshot_path, full_page=True) 
        return browser, page  

        # browser.close()

def encode_file_to_base64(screenshot_path: str) -> str:
    """
    Encode the contents of a local file as a Base64 (UTF-8) string.
    AI Agent tool metadata (for discovery):
    - tool_name: encode_file_to_base64
    - purpose: Convert a file on disk into a Base64-encoded text string for safe transport in JSON, logs, or API calls.
    - inputs:
        - screenshot_path (str): Absolute or relative path to the file to encode.
    - outputs:
        - encoded (str): Base64-encoded file contents without line breaks.
    - side_effects: Reads the file from disk and emits an info-level log message including the file path.
    - failure_modes: Missing file, permission denied, path is a directory, or other I/O errors.
    Args:
            screenshot_path (str): Path to the file to encode. Works with any binary or text file.
    Returns:
            str: Base64-encoded contents of the file as a UTF-8 string (standard Base64 alphabet, no newlines).
    Raises:
            FileNotFoundError: If the file does not exist.
            PermissionError: If the process lacks read permissions.
            IsADirectoryError: If the provided path is a directory.
            OSError: For other I/O-related errors while opening or reading the file.
            MemoryError: If the file is too large to be read into memory.
    Logging:
            Emits an info-level log line indicating that encoding is starting for the provided path.
    Notes:
            - Reads the entire file into memory; for very large files consider a streaming encoder.
            - Base64 is reversible and not a security mechanism; avoid using it as a substitute for encryption.
    Example:
            encoded = encode_file_to_base64("path/to/screenshot.png")
            # Use 'encoded' in an HTTP/JSON payload or store as text.
    """
        
    with open(screenshot_path, "rb") as file:
        # logger.level = logging.DEBUG  # Set the logging level to DEBUG
        logging.debug(f"Encoding file {screenshot_path} to base64")  # Log the encoding action
        encoded_string = base64.b64encode(file.read()).decode('utf-8')
        return encoded_string
    


def extract_elements_from_image(encoded_image: str)->dict:
    """
    AI Tool: extract_elements_from_image
    Extract HTML-like UI elements from a base64-encoded image using a vision-capable Ollama model.
    The model is instructed to return a JSON array of objects, each containing the fields:
    'tag', 'id', 'class', and 'text'. The function posts the image and prompt to OLLAMA_HOST,
    then parses and returns the model's JSON response as native Python objects.
    Parameters
    ----------
    encoded_image : str
        A base64-encoded image string (e.g., PNG/JPEG). This should be the raw base64 payload;
        include a data URI prefix only if the target model/server expects it.
    Returns
    -------
    dict
        A JSON-compatible Python object parsed from the model's response. Typically this is a
        list of element dictionaries like:
        [
          {"tag": "button", "id": "submit", "class": "btn btn-primary", "text": "Submit"},
          ...
        ]
    Side Effects
    ------------
    - Emits an INFO-level log message when extraction begins.
    External Dependencies / Configuration
    -------------------------------------
    - Requires global constants:
      - VISION_MODEL: Name of the Ollama vision model to invoke.
      - OLLAMA_HOST: Base URL for the Ollama server (e.g., http://localhost:11434).
    - HTTP POST to: {OLLAMA_HOST}/api/generate
      Payload keys: model, prompt, stream=False, images=[encoded_image], format="json"
    Raises
    ------
    requests.exceptions.RequestException
        If a network-related error occurs during the POST (e.g., connection errors).
    ValueError
        If response.json() fails due to a non-JSON HTTP body.
    json.JSONDecodeError
        If the model's "response" field is not valid JSON.
    KeyError
        If expected keys are missing from the server response.
    Notes for AI Agents / Tooling
    -----------------------------
    - Tool name: extract_elements_from_image
    - Input schema: {"encoded_image": "base64-string"}
    - Output schema (typical): [{"tag": "str", "id": "Optional[str]", "class": "Optional[str|list]", "text": "str"}]
    - Non-deterministic behavior may occur depending on the underlying model configuration.
    - Privacy: The encoded image is transmitted to OLLAMA_HOST; handle sensitive data accordingly.
    Example
    -------
    >>> elements = extract_elements_from_image(encoded_image)
    >>> # elements -> [{'tag': 'button', 'id': 'submit', 'class': 'btn btn-primary', 'text': 'Submit'}, ...]
    """
    # ENCODED_IMAGE = encoded_image
    PROMPT= (f"Extract all the HTML elements from the encoded image:"
             f"and return them as a JSON array of objects with 'tag', 'id', 'class', and 'text' fields.")
   
    logging.debug(f"Extracting elements from encoded image")
    payload = {
        "model": VISION_MODEL,
        "prompt": PROMPT,
        "stream": False,
        "images": [encoded_image],
        "format": "json",
    }
    response = requests.post(f"{OLLAMA_HOST}/api/generate", json=payload)
    response_json = json.loads(response.json().get("response", ""))

    # logging.info(f"Response JSON type: {type(response_json)}")
    # logging.info(f"Response JSON: {response_json}")
    return response_json

def generate_automation_code(vision_elements: dict, url) -> str:
    """
    Generate Python Playwright automation code for UI interactions using an AI model.
    This function acts as a code generation tool that takes UI vision elements and produces
    executable Playwright automation code. It's designed to be discoverable and usable by
    AI agents that need to automate web interactions.
    Args:
        vision_elements (dict): A dictionary containing detected UI elements from the interface,
                               typically including information about input fields, buttons, and
                               other interactive components (e.g., email field, password field,
                               login button).
    Returns:
        str: Generated Python Playwright code as a string that can be executed to perform
             the automation tasks. The code focuses on filling forms and clicking buttons
             based on the provided vision elements.
    Example:
        >>> elements = {"email_field": "input#email", "password_field": "input#password"}
        >>> code = generate_automation_code(elements)
        >>> print(code)  # Returns Playwright code for automation
    Note:
        - Requires OLLAMA_MODEL and OLLAMA_HOST to be configured
        - The function uses an external AI model API to generate the code
        - Generated code is returned without explanations or comments
        - Designed for AI agent discovery and autonomous automation workflows
    Tool Metadata:
        - Category: Code Generation
        - Purpose: Web UI Automation
        - Output Format: Python Playwright code
        - AI Agent Compatible: Yes
    """
    logging.debug(f"Generating automation code for vision elements")
    payload={
        "model": OLLAMA_MODEL,
        "prompt": (f"You are an automation agent. The user interface contains:{vision_elements}. Generate Python "
                   f"Playwright code to fill out the search box in the url {url}with the string 'AI based automation' and select the search button.\n"
                   f"Output only the Python code for the actions, no explanation.\n"
                   f"Provide only the code without any explanations."),
        "stream": False
    }
    response = requests.post(f"{OLLAMA_HOST}/api/generate",json=payload)
    automation_code = response.json().get("response", "")
    
    lines = automation_code.strip().splitlines()
    # Remove the first line if it starts with ``` (optionally with 'python')
    if lines and lines[0].strip().startswith("```"):
        lines = lines[1:]
    # Remove the last line if it is ```
    if lines and lines[-1].strip().startswith("```"):
        lines = lines[:-1]
    automation_code = "\n".join(lines)


    with open("generated_automation_code.py", "w") as code_file:
        code_file.write(automation_code)

    return automation_code

async def execute_automation_code(actions_code: str, url):
    """
    Execute Playwright automation code against a specified URL.
    This function dynamically generates and executes Playwright browser automation code
    in a headless Chromium browser. It wraps the provided actions code in an async
    context with proper browser lifecycle management.
    Args:
        actions_code (str): Python code containing Playwright actions to execute on the page.
                           This code will be inserted into the async function body and should
                           use the 'page' object for browser interactions.
                           Example: "await page.click('#submit-button')"
        url (str): The target URL to navigate to before executing the actions.
                  Should be a valid HTTP/HTTPS URL.
    Returns:
        None
    Raises:
        Exception: May raise various exceptions from Playwright operations or exec() execution,
                  including navigation errors, selector timeouts, or syntax errors in actions_code.
    Example:
        >>> actions = "await page.fill('#username', 'test')"
        >>> await execute_automation_code(actions, "https://example.com")
    Note:
        - Runs browser in headless mode for performance
        - Uses exec() with globals() scope - ensure actions_code is from trusted sources
        - Browser automatically closes after execution
        - Execution is logged at DEBUG level
    Tool Discovery Tags:
        - web automation
        - browser testing
        - playwright execution
        - dynamic code execution
        - headless browser"""
    logging.debug(f"Preparing to execute automation code on URL: {url}")
    local_code = f"""
    async def run():
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto(f\"{url}\")
            {actions_code}
            await browser.close()

    asyncio.run(run())
"""
    with open("local_code.py", "w") as code_file:
        code_file.write(local_code) 
    logging.debug(f"Executing automation code")
    exec(local_code, globals())
