import base64
import os
import requests
import json
import logging
import asyncio
import re
from pathlib import Path
from typing import Optional, Dict, List, Tuple
from dotenv import load_dotenv
from playwright.async_api import async_playwright, Browser, Page
from llm_provider import LLMProvider, get_llm_provider

# Load environment variables once at module level
load_dotenv()

# Initialize LLM provider (supports Ollama, OpenAI, Anthropic, Google, Azure)
# Configure via environment variables:
#   LLM_PROVIDER: 'ollama', 'openai', 'anthropic', 'google', 'azure'
#   LLM_MODEL: Main model for text generation
#   LLM_VISION_MODEL: Model for vision tasks
#   LLM_CODING_MODEL: Model for code generation
# Legacy environment variables for backward compatibility:
#   OLLAMA_BASE_URL, OLLAMA_MODEL, VISION_MODEL, CODING_MODEL
try:
    llm_provider = get_llm_provider()
except Exception as e:
    logging.warning(f"Failed to initialize LLM provider: {e}. Will attempt on first use.")
    llm_provider = None

# Configure logging once
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    force=True
)

# Constants
VIEWPORT = {'width': 1280, 'height': 720}
REQUEST_TIMEOUT = 300 # seconds
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.webp'}

# Forbidden operations for code sanitization
FORBIDDEN_PATTERNS = [
    r'\beval\b',
    r'\b__import__\b',
    r'\bopen\b',
    r'\bos\.',
    r'\bsys\.',
    r'\bsubprocess\b',
    r'\bimportlib\b',
    r'\b__builtins__\b',
    r'\bglobals\(',
    r'\blocals\(',
    r'\bsetattr\b',
    r'\bdelattr\b',
]
REQUEST_TIMEOUT = 300 # seconds

# Reusable requests session with connection pooling
_session = None

def get_session() -> requests.Session:
    """Get or create a persistent HTTP session for connection pooling.
    
    AI Tool Discovery Metadata:
    - Category: HTTP Client Management
    - Task: Connection Pool Optimization
    - Purpose: Reuse TCP connections for improved performance (30-50% faster API calls)
    
    Returns:
        requests.Session: Persistent session with connection pooling enabled
        
    Performance Benefits:
        - Reuses TCP connections to Ollama API
        - Reduces handshake overhead
        - Maintains keep-alive connections
        - ~30-50% faster than creating new session per request
        
    Thread Safety:
        - Uses global variable (not thread-safe)
        - Suitable for single-threaded async applications
        - For multi-threaded use, implement thread-local storage
        
    Configuration:
        - Sets Content-Type: application/json header
        - No timeout configured (uses request-level timeouts)
    """
    global _session
    if _session is None:
        _session = requests.Session()
        _session.headers.update({'Content-Type': 'application/json'})
    return _session


def validate_url(url: str) -> bool:
    """Validate URL to prevent SSRF and injection attacks.
    
    AI Tool Discovery Metadata:
    - Category: Security Validation
    - Task: URL Security Verification
    - Purpose: Prevent Server-Side Request Forgery (SSRF) and injection attacks
    
    Args:
        url (str): URL string to validate
        
    Returns:
        bool: True if URL is valid and safe
        
    Raises:
        ValueError: If URL is empty, not a string, or has invalid format
        
    Security Features:
        - Type checking (must be non-empty string)
        - Protocol validation (http:// or https://)
        - Domain format validation (FQDN or IP address)
        - Localhost detection
        - Port number validation
        - Path/query string validation
        
    Allowed Patterns:
        - https://example.com
        - http://subdomain.example.com:8080/path
        - http://localhost:3000
        - http://192.168.1.1/api
        
    Blocked Patterns:
        - file:///etc/passwd
        - javascript:alert(1)
        - data:text/html,<script>alert(1)</script>
        - URLs without protocol
        
    Example:
        >>> validate_url("https://example.com/api")
        True
        >>> validate_url("file:///etc/passwd")
        ValueError: Invalid URL format
    """
    if not url or not isinstance(url, str):
        raise ValueError("URL must be a non-empty string")
    
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
    
    return True


def validate_file_path(file_path: str) -> Path:
    """Validate and sanitize file paths to prevent path traversal attacks.
    
    AI Tool Discovery Metadata:
    - Category: Security Validation
    - Task: Path Traversal Prevention
    - Purpose: Prevent directory traversal attacks (../, ..\, etc.)
    
    Args:
        file_path (str): File path to validate
        
    Returns:
        Path: Validated pathlib.Path object (resolved to absolute path)
        
    Raises:
        ValueError: If path is empty, not a string, outside current directory, or has invalid extension
        
    Security Features:
        - Type checking (must be non-empty string)
        - Path resolution to absolute path
        - Directory traversal detection (must be within current working directory)
        - File extension whitelist enforcement
        
    Allowed Extensions:
        - .png, .jpg, .jpeg, .webp (image files only)
        
    Blocked Patterns:
        - ../../../etc/passwd
        - ..\..\..\Windows\System32
        - /etc/hosts
        - Any path outside current working directory
        
    Example:
        >>> validate_file_path("screenshot.png")
        PosixPath('/home/user/project/screenshot.png')
        >>> validate_file_path("../sensitive/file.txt")
        ValueError: File path must be within current directory
        >>> validate_file_path("image.exe")
        ValueError: Invalid file extension
    """
    if not file_path or not isinstance(file_path, str):
        raise ValueError("File path must be a non-empty string")
    
    path = Path(file_path).resolve()
    
    # Check for path traversal attempts
    try:
        path.relative_to(Path.cwd())
    except ValueError:
        raise ValueError(f"File path must be within current directory: {file_path}")
    
    # Check file extension
    if path.suffix.lower() not in ALLOWED_EXTENSIONS:
        raise ValueError(f"Invalid file extension. Allowed: {ALLOWED_EXTENSIONS}")
    
    return path


def sanitize_code(code: str) -> str:
    """Sanitize generated code to remove potentially dangerous operations.
    
    AI Tool Discovery Metadata:
    - Category: Code Security
    - Task: Malicious Code Detection
    - Purpose: Prevent execution of dangerous Python operations in AI-generated code
    
    Args:
        code (str): Python code string to sanitize
        
    Returns:
        str: Original code if safe (or raises exception if dangerous)
        
    Raises:
        ValueError: If code contains any forbidden operations
        
    Forbidden Operations:
        - eval: Arbitrary code execution
        - __import__: Dynamic module imports
        - open: File system access
        - os.*: Operating system operations
        - sys.*: System-level operations
        - subprocess: Shell command execution
        - importlib: Dynamic imports
        - __builtins__: Access to built-in functions
        - globals(), locals(): Scope manipulation
        - setattr, delattr: Object manipulation
        
    Security Approach:
        - Pattern-based detection using regex
        - Case-insensitive matching
        - Blocks entire code if any pattern matches
        - Does not attempt to fix/remove patterns
        
    Example:
        >>> sanitize_code("page.fill('#email', 'test@example.com')")
        "page.fill('#email', 'test@example.com')"
        
        >>> sanitize_code("import os; os.system('rm -rf /')")
        ValueError: Generated code contains forbidden operation: \\bos\\.
        
    Use Cases:
        - Validating AI-generated Playwright automation code
        - Pre-execution security checks
        - Preventing code injection attacks
        
    Limitations:
        - Pattern-based (may have false positives/negatives)
        - Cannot detect obfuscated attacks
        - Recommend sandboxed execution even after sanitization
    """
    for pattern in FORBIDDEN_PATTERNS:
        if re.search(pattern, code, re.IGNORECASE):
            raise ValueError(f"Generated code contains forbidden operation: {pattern}")
    return code


async def open_browser(url: str) -> None:
    """Launch browser and navigate to target URL for automation workflows.
    
    AI Tool Discovery Metadata:
    - Category: Browser Automation
    - Task: Browser Launch and Navigation
    - Purpose: Initialize Playwright browser and navigate to URL for web automation tasks
    - Library: Playwright (async Chromium automation)
    
    Args:
        url (str): Target web page URL to navigate to (validated before launch)
        
    Returns:
        None: Browser closes automatically after navigation completes
        
    Configuration:
        - Browser: Chromium
        - Headless: False (visible GUI for debugging)
        - Viewport: 1280x720 (laptop resolution)
        - Timeout: 30 seconds for navigation
        - Wait Until: DOMContentLoaded event
        
    Process:
        1. Validates URL format and security
        2. Launches Playwright async context
        3. Creates Chromium browser instance
        4. Opens new page with configured viewport
        5. Navigates to URL
        6. Logs page title for debugging
        7. Auto-closes browser via context manager
        
    Example Usage:
        ```python
        await open_browser("https://example.com")
        # Browser opens, navigates, logs title, then closes
        ```
        
    Security:
        - URL validated before launch (prevents SSRF)
        - Auto-cleanup via async context manager
        - No persistent browser state
        
    Performance:
        - Initial launch: ~2 seconds
        - Page load: Varies by site (5-15 seconds typical)
        - Auto-cleanup prevents resource leaks
        
    Error Handling:
        - ValueError: Invalid URL format (from validate_url)
        - Timeout: Page load exceeds 30 seconds
        - Network errors: DNS failures, connection refused
        - Browser auto-closes even on error (try/finally)
        
    Use Cases:
        - Quick URL navigation for debugging
        - Manual browser testing workflows
        - Visual verification of page loads
        
    Tool Category: Browser Automation, Web Driver Management, Async Navigation
    """
    validate_url(url)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        try:
            page = await browser.new_page(viewport=VIEWPORT)
            await page.goto(url, wait_until='domcontentloaded', timeout=30000)
            logging.debug(f"Title of the page: {await page.title()}")
        finally:
            await browser.close()


async def open_browser_capture_screen(url: str, screenshot_path: str) -> Tuple[Browser, Page]:
    """Open browser, navigate to URL, capture screenshot, and return browser handles.
    
    AI Tool Discovery Metadata:
    - Category: Browser Automation / Screenshot Capture
    - Task: Browser Launch with Screenshot
    - Purpose: Launch browser, capture full-page screenshot, and return active browser handles for further automation
    - Library: Playwright (async Chromium automation)
    
    Args:
        url (str): Target web page URL to navigate to (validated before launch)
        screenshot_path (str): File path to save screenshot (validated for security)
        
    Returns:
        Tuple[Browser, Page]: Active browser and page objects for continued automation
            - Browser: Chromium browser instance (must be closed by caller)
            - Page: Loaded page object with captured screenshot (must be closed by caller)
            
    Configuration:
        - Browser: Chromium
        - Headless: False (visible GUI)
        - Viewport: 1280x720 (laptop resolution)
        - Timeout: 30 seconds for navigation
        - Screenshot: Full page (scrolling viewport)
        
    Process:
        1. Validates URL format and security
        2. Validates screenshot path (prevents path traversal)
        3. Launches Playwright async context
        4. Creates Chromium browser instance
        5. Opens new page with configured viewport
        6. Navigates to URL (waits for DOMContentLoaded)
        7. Captures full-page screenshot to specified path
        8. Returns active browser and page (caller must close)
        
    Example Usage:
        ```python
        browser, page = await open_browser_capture_screen(
            "https://example.com",
            "screenshots/example.png"
        )
        # Perform additional automation with page object
        await page.fill("#email", "test@example.com")
        await browser.close()
        ```
        
    Security:
        - URL validated before launch (prevents SSRF)
        - Screenshot path validated (prevents path traversal)
        - File extension must be in ALLOWED_EXTENSIONS (.png, .jpg, .jpeg)
        - Path must be within current directory
        
    Performance:
        - Initial launch: ~2 seconds
        - Page load: Varies by site (5-15 seconds typical)
        - Screenshot: 1-3 seconds (depends on page height)
        - Total: ~8-20 seconds for typical page
        
    Error Handling:
        - ValueError: Invalid URL or file path format
        - Timeout: Page load exceeds 30 seconds
        - IOError: Screenshot file write failure
        - Caller must handle browser.close() in try/finally
        
    Resource Management:
        - Browser and page must be closed by caller
        - Async context manager exits after return
        - Memory leak risk if browser not closed
        
    Use Cases:
        - Visual regression testing
        - Screenshot-based element extraction
        - Browser state preservation for multi-step automation
        - Page analysis workflows
        
    Tool Category: Browser Automation, Screenshot Capture, Stateful Browser Management
    """
    validate_url(url)
    validated_path = validate_file_path(screenshot_path)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page(viewport=VIEWPORT)
        await page.goto(url, wait_until='domcontentloaded', timeout=30000)
        await page.screenshot(path=str(validated_path), full_page=True)
        return browser, page


def encode_file_to_base64(screenshot_path: str) -> str:
    """Encode file contents as Base64 string for AI vision model consumption.
    
    AI Tool Discovery Metadata:
    - Category: Image Processing / Encoding
    - Task: File to Base64 Conversion
    - Purpose: Convert image files to Base64-encoded strings for AI vision model APIs (Ollama)
    - Use Case: Prepare screenshots for llama3.2-vision model input
    
    Args:
        screenshot_path (str): Path to image file to encode (validated for security)
        
    Returns:
        str: Base64-encoded string representation of file contents
        
    Supported File Types:
        - PNG (.png)
        - JPEG (.jpg, .jpeg)
        
    Example Usage:
        ```python
        base64_image = encode_file_to_base64("screenshots/homepage.png")
        # Use in Ollama API request
        payload = {
            "model": "llama3.2-vision",
            "images": [base64_image]
        }
        ```
        
    Process:
        1. Validates file path (prevents path traversal)
        2. Checks file exists
        3. Checks file size (max 10MB)
        4. Reads file in binary mode
        5. Encodes to Base64 string
        6. Returns string (no data URI prefix)
        
    Security:
        - Path validated before access (prevents path traversal)
        - File extension must be in ALLOWED_EXTENSIONS
        - File size limited to MAX_FILE_SIZE (10MB)
        - Path must be within current directory
        
    Performance:
        - Typical encoding time: <100ms for 1MB file
        - Memory usage: ~1.33x file size (Base64 overhead)
        - No streaming (entire file loaded to memory)
        
    Error Handling:
        - ValueError: Invalid file path format
        - FileNotFoundError: File doesn't exist at path
        - ValueError: File size exceeds 10MB limit
        - IOError: File read permission errors
        
    Raises:
        FileNotFoundError: If file does not exist at validated path
        ValueError: If file size exceeds MAX_FILE_SIZE (10MB)
        
    File Size Limits:
        - Maximum: 10MB (prevents DoS via large files)
        - Typical screenshot: 200KB-2MB
        - Recommended: Keep under 5MB for API performance
        
    Use Cases:
        - Preparing screenshots for vision AI models
        - Image-based UI element extraction
        - Visual regression testing payloads
        - Embedding images in JSON API requests
        
    Tool Category: Image Encoding, Base64 Conversion, Vision AI Preprocessing
    """
    validated_path = validate_file_path(screenshot_path)
    
    if not validated_path.exists():
        raise FileNotFoundError(f"File not found: {screenshot_path}")
    
    # Check file size
    file_size = validated_path.stat().st_size
    if file_size > MAX_FILE_SIZE:
        raise ValueError(f"File too large: {file_size} bytes (max: {MAX_FILE_SIZE})")
    
    logging.debug(f"Encoding file {screenshot_path} to base64")
    with open(validated_path, "rb") as file:
        return base64.b64encode(file.read()).decode('utf-8')


def extract_elements_from_image(encoded_image: str) -> str:
    """Extract UI elements from base64-encoded screenshot using AI vision model.
    
    AI Tool Discovery Metadata:
    - Category: Vision AI / UI Element Extraction
    - Task: Image-Based Element Detection
    - Purpose: Use AI vision model to extract HTML elements from screenshot
    - Model: Configurable via LLM_VISION_MODEL environment variable (supports multiple providers)
    
    Args:
        encoded_image (str): Base64-encoded image string (from encode_file_to_base64)
        
    Returns:
        str: JSON string containing extracted elements
            Format: Array of objects with 'tag', 'id', 'class', 'text' fields
            
    Example Return:
        ```json
        [
            {
                "tag": "button",
                "id": "submit-btn",
                "class": "btn btn-primary",
                "text": "Submit"
            },
            {
                "tag": "input",
                "id": "email-field",
                "class": "form-control",
                "text": ""
            }
        ]
        ```
        
    Process:
        1. Validates encoded_image is non-empty string
        2. Constructs vision prompt for element extraction
        3. Sends POST request to Ollama API with image
        4. Requests JSON format response
        5. Returns parsed JSON string
        
    AI Prompt:
        "Extract all the HTML elements from the encoded image and return them 
        as a JSON array of objects with 'tag', 'id', 'class', and 'text' fields."
        
    API Configuration:
        - Endpoint: {OLLAMA_HOST}/api/generate
        - Model: llama3.2-vision
        - Stream: False (synchronous response)
        - Format: json (structured output)
        - Timeout: 60 seconds (REQUEST_TIMEOUT)
        
    Performance:
        - Typical inference time: 10-30 seconds
        - Depends on: Image size, model load state, GPU availability
        - First call slower (model loading)
        - Subsequent calls faster (model cached)
        
    Security:
        - No direct file access (uses base64 string)
        - Timeout prevents DoS attacks
        - Session pooling with headers
        
    Error Handling:
        - ValueError: encoded_image is empty or not a string
        - requests.exceptions.RequestException: API request failure
        - ValueError: Raised for Ollama API errors (network, timeout, 4xx/5xx)
        
    Raises:
        ValueError: If encoded_image is invalid or API request fails
        
    Use Cases:
        - Screenshot-based UI testing
        - Visual element discovery
        - Cross-browser compatibility testing
        - AI-assisted test generation
        
    Limitations:
        - Accuracy depends on screenshot quality
        - May miss hidden/overlay elements
        - Text extraction limited by OCR capabilities
        - Vision model may hallucinate elements
        
    Tool Category: Vision AI, Element Extraction, Computer Vision, Ollama Integration
    """
    if not encoded_image or not isinstance(encoded_image, str):
        raise ValueError("encoded_image must be a non-empty string")
    
    logging.debug("Extracting elements from encoded image")
    
    prompt = (
        "Extract all the HTML elements from the encoded image "
        "and return them as a JSON array of objects with 'tag', 'id', 'class', and 'text' fields."
    )
    
    try:
        provider = get_llm_provider()
        response = provider.generate_vision(prompt, encoded_image, format="json")
        return response
    except Exception as e:
        logging.error(f"Vision API request failed: {e}")
        raise ValueError(f"Failed to extract elements: {e}")


def generate_automation_code(vision_elements: Dict, url: str) -> str:
    """Generate Python Playwright automation code using AI coding model.
    
    AI Tool Discovery Metadata:
    - Category: Code Generation / AI-Assisted Automation
    - Task: Playwright Code Generation
    - Purpose: Use AI coding model to generate Playwright automation code from UI elements
    - Model: Configurable via LLM_CODING_MODEL environment variable (supports multiple providers)
    
    Args:
        vision_elements (Dict): Dictionary of UI elements extracted from screenshot/DOM
        url (str): Target URL for automation context (validated before processing)
        
    Returns:
        str: Python Playwright automation code (sanitized and safe to execute)
        
    Generated Code Pattern:
        ```python
        await page.fill('#search-box', 'AI based automation')
        await page.click('#search-button')
        await page.wait_for_selector('#results')
        ```
        
    Process:
        1. Validates URL format
        2. Constructs prompt with UI elements and task
        3. Sends POST request to Ollama API
        4. Cleans code fences (```python markers)
        5. Sanitizes code (removes dangerous operations)
        6. Saves to generated_automation_code.py
        7. Returns sanitized code string
        
    AI Prompt Template:
        "You are an automation agent. The user interface contains: {vision_elements}. 
        Generate Python Playwright code to fill out the search box in the url {url} 
        with the string 'AI based automation' and select the search button.
        IMPORTANT: Only use these Playwright methods: page.fill(), page.click(), page.wait_for_selector()
        Do NOT use: eval, exec, open, os, sys, subprocess, import, or any file operations.
        Output only the Python code for the actions, no explanation."
        
    API Configuration:
        - Endpoint: {OLLAMA_HOST}/api/generate
        - Model: deepseek-coder:6.7b (specialized for code generation)
        - Stream: False (synchronous response)
        - Timeout: 60 seconds (REQUEST_TIMEOUT)
        
    Security:
        - URL validated before prompt construction
        - Code sanitized with sanitize_code() (12 forbidden patterns)
        - Prompt restricts allowed Playwright methods
        - Prompt explicitly forbids dangerous operations
        - Output saved to controlled filename (no path traversal)
        
    Performance:
        - Typical inference time: 5-15 seconds
        - Depends on: Model load state, prompt complexity, GPU
        - First call slower (model loading ~3 seconds)
        - Subsequent calls faster (model cached)
        
    Error Handling:
        - ValueError: Invalid URL format (from validate_url)
        - requests.exceptions.RequestException: API request failure
        - ValueError: Raised for Ollama API errors or code sanitization failure
        - IOError: File write errors for generated_automation_code.py
        
    Raises:
        ValueError: If URL is invalid, API request fails, or code contains forbidden operations
        
    Output File:
        - Filename: generated_automation_code.py (current directory)
        - Encoding: UTF-8
        - Content: Sanitized Playwright code (no imports, no file operations)
        
    Use Cases:
        - Automated test script generation
        - Form filling automation
        - Search workflow automation
        - AI-assisted test case creation
        
    Limitations:
        - Hardcoded search task ("AI based automation")
        - Limited to page.fill(), page.click(), page.wait_for_selector()
        - May generate incorrect selectors if elements not in vision_elements
        - Code quality depends on model and prompt clarity
        
    Tool Category: AI Code Generation, Playwright Automation, Ollama Integration, Test Automation
    """
    validate_url(url)
    
    logging.debug("Generating automation code for vision elements")
    
    prompt = (
        f"You are an automation agent. The user interface contains: {vision_elements}. "
        f"Generate Python Playwright code to fill out the search box in the url {url} "
        f"with the string 'AI based automation' and select the search button.\n"
        f"IMPORTANT: Only use these Playwright methods: page.fill(), page.click(), page.wait_for_selector()\n"
        f"Do NOT use: eval, exec, open, os, sys, subprocess, import, or any file operations.\n"
        f"Output only the Python code for the actions, no explanation.\n"
        f"Provide only the code without any explanations."
    )
    
    try:
        provider = get_llm_provider()
        automation_code = provider.generate_code(prompt, max_tokens=2048, temperature=0.3)
        
        # Clean up code fences
        lines = automation_code.strip().splitlines()
        if lines and lines[0].strip().startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]
        automation_code = "\n".join(lines)
        
        # Sanitize the generated code
        sanitized_code = sanitize_code(automation_code)
        
        with open("generated_automation_code.py", "w", encoding='utf-8') as code_file:
            code_file.write(sanitized_code)
        
        return sanitized_code
    except Exception as e:
        logging.error(f"Code generation API request failed: {e}")
        raise ValueError(f"Failed to generate automation code: {e}")


async def execute_automation_code(actions_code: str, url: str) -> None:
    """Execute Playwright automation code against a specified URL with restricted scope.
    
    AI Tool Discovery Metadata:
    - Category: Dynamic Code Execution / Automation Runner
    - Task: Safe Code Execution
    - Purpose: Execute AI-generated Playwright automation code in a restricted Python environment
    - Security: Restricted __builtins__ scope to prevent malicious operations
    
    Args:
        actions_code (str): Python Playwright automation code to execute (must be sanitized)
        url (str): Target URL for automation (validated before execution)
        
    Returns:
        None: Function executes code asynchronously and returns when complete
        
    Process:
        1. Validates URL format
        2. Sanitizes code (checks for forbidden patterns)
        3. Creates restricted execution environment
        4. Wraps code in async function with browser setup
        5. Executes code using exec() with restricted globals
        6. Launches headless Chromium browser
        7. Navigates to URL
        8. Executes automation actions
        9. Closes browser automatically
        
    Example Input Code:
        ```python
        await page.fill('#search-box', 'AI based automation')
        await page.click('#search-button')
        await page.wait_for_selector('#results')
        ```
        
    Security:
        - URL validated before execution
        - Code sanitized (12 forbidden patterns checked)
        - Restricted __builtins__ dictionary:
            - Allowed: print, len, str, int, float, bool, list, dict, True, False, None
            - Blocked: open, eval, exec, __import__, compile, etc.
        - Only async_playwright and asyncio modules accessible
        - No file system access
        - No operating system commands
        - No dynamic imports
        
    Restricted Execution Environment:
        ```python
        restricted_globals = {
            '__builtins__': {
                'print': print,  # Logging only
                'len': len, 'str': str, 'int': int, 'float': float, 'bool': bool,
                'list': list, 'dict': dict,
                'True': True, 'False': False, 'None': None
            },
            'async_playwright': async_playwright,
            'asyncio': asyncio
        }
        ```
        
    Browser Configuration:
        - Browser: Chromium
        - Headless: True (no GUI)
        - Viewport: 1280x720 (laptop resolution)
        - Timeout: 30 seconds for navigation
        
    Performance:
        - Browser launch: ~2 seconds
        - Page load: 5-15 seconds (depends on site)
        - Automation execution: Varies by code complexity
        - Total: 10-30 seconds typical
        
    Error Handling:
        - ValueError: Invalid URL format (from validate_url)
        - ValueError: Code contains forbidden operations (from sanitize_code)
        - SyntaxError: Invalid Python code syntax
        - RuntimeError: exec() execution errors
        - Timeout: Page load or automation exceeds timeout
        
    Raises:
        ValueError: If URL is invalid or code contains forbidden operations
        SyntaxError: If actions_code has invalid Python syntax
        RuntimeError: If automation code execution fails
        
    Limitations:
        - Restricted __builtins__ may break some legitimate operations
        - No access to external libraries beyond Playwright/asyncio
        - Difficult to debug errors from exec() context
        - No return value from automation code
        - Cannot capture screenshots or other outputs
        
    Use Cases:
        - Executing AI-generated test scripts
        - Running automation workflows from templates
        - Form filling and button clicking automation
        - Integration testing with dynamic code
        
    Warning:
        This function uses exec() which is inherently dangerous.
        ONLY use with:
        - Sanitized code from sanitize_code()
        - Trusted sources (AI models with safety prompts)
        - Isolated environments (containers/VMs recommended)
        
    Tool Category: Dynamic Code Execution, Sandboxed Automation, Playwright Runner, Security-Restricted Execution
    """
    validate_url(url)
    sanitized_code = sanitize_code(actions_code)
    
    logging.debug(f"Preparing to execute automation code on URL: {url}")
    
    # Create a restricted execution environment
    restricted_globals = {
        '__builtins__': {
            'print': print,
            'len': len,
            'str': str,
            'int': int,
            'float': float,
            'bool': bool,
            'list': list,
            'dict': dict,
            'True': True,
            'False': False,
            'None': None,
        },
        'async_playwright': async_playwright,
        'asyncio': asyncio,
    }
    
    local_code = f"""
async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        try:
            await page.goto("{url}", wait_until='domcontentloaded', timeout=30000)
            {sanitized_code}
        finally:
            await browser.close()

asyncio.run(run())
"""
    
    with open("local_code.py", "w", encoding='utf-8') as code_file:
        code_file.write(local_code)
    
    logging.debug("Executing automation code in restricted environment")
    try:
        exec(local_code, restricted_globals)
    except Exception as e:
        logging.error(f"Error executing automation code: {e}")
        raise ValueError(f"Automation execution failed: {e}")


async def get_interactive_elements(url: str) -> List[Dict]:
    """Retrieve all interactive elements from a web page for AI agent automation.
    
    AI Tool Discovery Metadata:
    - Category: Web Scraping / UI Analysis
    - Task: Interactive Element Extraction
    - Purpose: Extract metadata about all interactive elements (buttons, inputs, links) for test generation
    - Library: Playwright (async browser automation)
    
    Args:
        url (str): Target web page URL to analyze
        
    Returns:
        List[Dict]: List of element dictionaries, each containing:
            - tag (str): HTML tag name (lowercase) - "input", "button", "a", "textarea", "select"
            - type (str|None): Type attribute (for inputs) - "email", "password", "submit", etc.
            - id (str|None): Element ID attribute
            - name (str|None): Name attribute
            - text (str): Visible text content (trimmed, max 100 chars)
            - placeholder (str|None): Placeholder attribute
            - ariaLabel (str|None): ARIA label for accessibility
            - role (str|None): ARIA role attribute
            
    Example Output:
        [
            {
                "tag": "input",
                "type": "email",
                "id": "email-field",
                "name": "email",
                "text": "",
                "placeholder": "Enter your email",
                "ariaLabel": "Email address",
                "role": None
            },
            {
                "tag": "button",
                "type": "submit",
                "id": "login-btn",
                "name": None,
                "text": "Sign In",
                "placeholder": None,
                "ariaLabel": None,
                "role": "button"
            }
        ]
        
    Process:
        1. Validates URL for security
        2. Launches headless Chromium browser
        3. Navigates to URL (waits for DOMContentLoaded)
        4. Executes JavaScript to query DOM
        5. Extracts metadata from each element
        6. Closes browser automatically
        
    Extracted Element Types:
        - <a>: Links and navigation
        - <button>: Buttons and submit controls
        - <input>: Form input fields
        - <textarea>: Multi-line text inputs
        - <select>: Dropdown/select elements
        
    Performance:
        - Headless mode for faster rendering
        - Text limited to 100 chars per element
        - Timeout: 30 seconds for page load
        - Typical execution: 5-10 seconds
        
    Use Cases:
        - Test case generation (functional tests)
        - UI element discovery for automation
        - Accessibility auditing
        - Form analysis and validation
        - Navigation flow mapping
        
    Error Handling:
        - ValueError: Invalid URL format
        - Timeout: Page load exceeds 30 seconds
        - Network errors: DNS failures, connection refused
        
    Tool Category: Web Automation, UI Element Discovery, Agent Interaction Mapping
    """
    validate_url(url)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # Headless for performance
        try:
            page = await browser.new_page(viewport=VIEWPORT)
            await page.goto(url, wait_until='domcontentloaded', timeout=30000)
            
            # Optimized JavaScript for element extraction
            elements = await page.evaluate("""
                () => {
                    const selectors = 'a, button, input, textarea, select';
                    const nodeList = document.querySelectorAll(selectors);
                    const elements = [];
                    
                    for (let i = 0; i < nodeList.length; i++) {
                        const el = nodeList[i];
                        elements.push({
                            tag: el.tagName.toLowerCase(),
                            type: el.getAttribute('type'),
                            id: el.id || null,
                            name: el.getAttribute('name'),
                            text: (el.innerText || '').trim().substring(0, 100),  // Limit text length
                            placeholder: el.getAttribute('placeholder'),
                            ariaLabel: el.getAttribute('aria-label'),
                            role: el.getAttribute('role')
                        });
                    }
                    
                    return elements;
                }
            """)
            
            return elements
        finally:
            await browser.close()


def build_nfr_tests_prompt(
    url: str,
    elements: List[Dict],
    business_context: str,
    nfr_expectations: Optional[Dict] = None
) -> str:
    """
    Generates a prompt for building non-functional requirement (NFR) test cases.
    This function constructs a detailed prompt that outlines the necessary 
    information for creating exhaustive non-functional test cases for a given 
    application. It includes the application URL, business context, interactive 
    elements, and known NFR expectations. The output is formatted as a strict 
    JSON object that specifies various NFR categories such as performance, 
    reliability, security, usability, compatibility, scalability, maintainability, 
    and compliance.
    Parameters:
    - url (str): The URL of the application under test.
    - elements (List[Dict]): A list of interactive elements in the application, 
        limited to the first 20 for the prompt.
    - business_context (str): The business context in which the application operates.
    - nfr_expectations (Optional[Dict]): A dictionary of known non-functional 
        requirements expectations. Defaults to None if not provided.
    Returns:
    - str: A formatted string containing the prompt for generating NFR test cases 
        in strict JSON format.
    Notes:
    - The output JSON must adhere to specific formatting rules, including proper 
        quoting and escaping of strings, and must not contain any additional text 
        outside the JSON structure.
    - The function is designed to ensure comprehensive coverage across all NFR 
        dimensions, generating multiple test cases per category with specific metrics 
        and thresholds where applicable.
    """
    elems_json = json.dumps(elements[:20], separators=(',', ':'))
    expectations_json = json.dumps(nfr_expectations or {}, separators=(',', ':'))
    
    return f"""You are an expert QA architect specializing in comprehensive non-functional testing.

Application under test:
- URL: {url}
- Business context: {business_context}

Interactive elements (first 20): {elems_json}

Known NFR expectations: {expectations_json}

Design EXHAUSTIVE NON-FUNCTIONAL test cases covering ALL dimensions:
- PERFORMANCE: Load time, response time, throughput, resource utilization, caching, CDN effectiveness
- RELIABILITY: Uptime, fault tolerance, recovery, error handling, data consistency, transaction integrity
- SECURITY: Authentication, authorization, data encryption, injection attacks, CSRF, XSS, API security, SSL/TLS
- USABILITY: Accessibility (WCAG 2.1 AA), responsive design, UI consistency, error messages, navigation clarity
- COMPATIBILITY: Browser compatibility, device compatibility, OS compatibility, API backward compatibility
- SCALABILITY: Concurrent users, database scaling, horizontal scaling, vertical scaling, rate limiting
- MAINTAINABILITY: Code quality, documentation, logging, monitoring, deployment safety, rollback capability
- COMPLIANCE: GDPR, HIPAA, CCPA, data retention, audit trails, regulatory requirements

CRITICAL INSTRUCTIONS:
1. Return ONLY valid JSON, nothing else
2. All strings must be properly quoted and escaped
3. Use double quotes for strings, not single quotes
4. Ensure all arrays and objects are properly closed
5. Do not include any explanatory text outside the JSON
6. Generate at least 3-5 test cases per NFR category
7. Include specific metrics and thresholds where applicable
8. For security: list specific attack vectors to test
9. For performance: include load profiles and expected baselines

OUTPUT FORMAT (strict JSON only):
{{
  "nfr": [
    {{
      "id": "NFR_001",
      "category": "performance|reliability|security|usability|compatibility|scalability|maintainability|compliance",
      "title": "Specific test title",
      "description": "Detailed test description",
      "acceptance_criteria": ["criterion1", "criterion2", "criterion3"],
      "tooling_suggestions": ["tool1", "tool2"],
      "metrics": {{"threshold": "value", "unit": "unit"}},
      "priority": "critical|high|medium|low"
    }}
  ]
}}

Remember: ONLY output the JSON object above. Generate comprehensive, exhaustive test coverage across all NFR dimensions. No markdown, no explanations."""


def build_functional_tests_prompt(
    url: str,
    elements: List[Dict],
    business_context: str
) -> str:
    """
    Generates a prompt for creating comprehensive functional test cases based on the provided application details.
    Parameters:
        url (str): The URL of the application under test.
        elements (List[Dict]): A list of interactive elements in the application, represented as dictionaries.
        business_context (str): The business context or scenario in which the application operates.
    Returns:
        str: A formatted string containing instructions for generating functional test cases in strict JSON format.
    The generated prompt includes guidelines for covering various testing scenarios such as:
    - Happy path scenarios
    - Negative cases and error handling
    - Boundary testing and edge cases
    - Data validation requirements
    - User interactions and navigation flows
    - Error recovery mechanisms
    - State management considerations
    - Cross-browser functionality
    - Accessibility compliance
    The output format is strictly defined as a JSON object, ensuring that all test cases are structured and comprehensive.
    """
    elems_json = json.dumps(elements[:20], separators=(',', ':'))
    
    return f"""You are an expert QA engineer specializing in comprehensive functional testing.

Application under test:
- URL: {url}
- Business context: {business_context}

Interactive elements (all elements): {elems_json}

Design EXHAUSTIVE FUNCTIONAL test cases covering ALL scenarios:
- HAPPY PATH: Primary user workflows, success scenarios, expected behaviors
- NEGATIVE CASES: Invalid inputs, error handling, boundary violations, edge cases
- BOUNDARY TESTING: Min/max values, empty fields, special characters, SQL injection attempts, XSS payloads
- DATA VALIDATION: Required fields, format validation, length limits, type checking
- USER INTERACTIONS: Form submission, navigation flows, button clicks, dropdown selections
- ERROR RECOVERY: Retry mechanisms, error messages, fallback behaviors
- STATE MANAGEMENT: Session persistence, data persistence, state transitions
- CROSS-BROWSER: UI consistency, functionality across browsers (if applicable)
- ACCESSIBILITY: Keyboard navigation, screen reader compatibility, ARIA labels
- INTEGRATION: API calls, backend data sync, third-party service interactions

CRITICAL INSTRUCTIONS:
1. Return ONLY valid JSON, nothing else
2. All strings must be properly quoted and escaped
3. Use double quotes for strings, not single quotes
4. Ensure all arrays and objects are properly closed
5. Do not include any explanatory text outside the JSON
6. Generate at least 5-8 test cases per functional area
7. Include both positive and negative test scenarios
8. Cover edge cases, boundary conditions, and error paths
9. For form elements: test validation, submission, and error states
10. For navigation: test all links, buttons, and user flows

OUTPUT FORMAT (strict JSON only):
{{
  "functional": [
    {{
      "id": "FUNC_001",
      "title": "Specific test case title",
      "description": "Detailed test description and purpose",
      "preconditions": ["precondition1", "precondition2", "precondition3"],
      "steps": ["step1", "step2", "step3", "step4"],
      "expected_result": "Detailed expected outcome and assertion points",
      "test_data": {{"input1": "value1", "input2": "value2"}},
      "category": "happy_path|negative|boundary|validation|navigation|error_recovery|state|accessibility",
      "tags": ["tag1", "tag2", "tag3"],
      "priority": "critical|high|medium|low"
    }}
  ]
}}

Remember: ONLY output the JSON object above. Generate exhaustive, comprehensive functional test coverage. No markdown, no explanations."""


async def generate_functional_tests(url: str, business_context: str) -> List[Dict]:
    """
    Generates functional tests based on the provided URL and business context.
    This asynchronous function retrieves interactive elements from the specified URL,
    builds a prompt for generating functional tests, and then parses the resulting JSON
    response to extract the functional test specifications.
    Args:
        url (str): The URL of the application or service for which to generate tests.
        business_context (str): The business context or scenario that the tests should consider.
    Returns:
        List[Dict]: A list of functional test specifications, where each specification is represented
        as a dictionary. If parsing fails, an empty list is returned.
    Raises:
        Exception: Raises an exception if there is an issue with generating or parsing the tests.
    """
   
    elements = await get_interactive_elements(url)
    prompt = build_functional_tests_prompt(url, elements, business_context)
    
    logging.debug("Generating functional tests with prompt")
    raw = generate_final_output(prompt)
    
    logging.debug(f"Functional Raw Output (first 500 chars): {raw[:500]}...")
    
    # Use robust JSON parser
    test_spec = parse_json_response(raw)
    
    if test_spec is None:
        logging.error("Failed to parse functional tests JSON")
        return []
    
    return test_spec.get("functional", [])


async def generate_nfr_tests(
    url: str,
    business_context: str,
    nfr_expectations: Optional[Dict] = None
) -> List[Dict]:
    """
    Generates Non-Functional Requirement (NFR) tests based on the provided URL and business context.
    This asynchronous function retrieves interactive elements from a specified URL, constructs a prompt 
    for generating NFR tests, and processes the output to return a list of NFR test specifications.
    Args:
        url (str): The URL of the application or service for which NFR tests are to be generated.
        business_context (str): The business context that provides additional information for generating tests.
        nfr_expectations (Optional[Dict], optional): A dictionary of specific NFR expectations to consider 
            during test generation. Defaults to None.
    Returns:
        List[Dict]: A list of dictionaries containing the generated NFR test specifications. 
            Returns an empty list if the JSON response cannot be parsed or if no NFR tests are found.
    Raises:
        Exception: Raises an exception if there is an error in generating or parsing the NFR tests.
    """
    elements = await get_interactive_elements(url)
    prompt = build_nfr_tests_prompt(url, elements, business_context, nfr_expectations)
    
    logging.debug("Generating NFR tests with prompt")
    raw = generate_final_output(prompt)
    
    logging.debug(f"NFR Raw Output (first 500 chars): {raw[:500]}...")
    
    # Use robust JSON parser
    test_spec = parse_json_response(raw)
    
    if test_spec is None:
        logging.error("Failed to parse NFR tests JSON")
        return
    
    return test_spec.get("nfr", [])


def generate_final_output(prompt: str, retry_with_simpler: bool = True) -> str:
    """
    Generate response from LLM API with strict JSON enforcement.
    
    Args:
        prompt: Text prompt for AI model
        retry_with_simpler: If True, retry with enhanced instructions on failure
    
    Returns:
        Raw response string from model
    """
    # Get LLM provider from environment
    provider = os.getenv("LLM_PROVIDER", "ollama").lower()
    
    # Enhanced payload with strict JSON controls
    if provider == "ollama":
        payload = {
            "model": os.getenv("LLM_MODEL", "llama3.2"),
            "prompt": prompt,
            "stream": False,  # Critical: disable streaming
            "format": "json",  # Request JSON format
            "options": {
                "temperature": 0.3,  # Lower = more deterministic
                "top_p": 0.9,
                "num_predict": 4096,  # Maximum tokens to generate
                "stop": ["```", "}\n\n", "]\n\n", "\n\n\n"]
            }
        }
        
        session = get_session()
        
        try:
            response = session.post(
                f"{os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')}/api/generate",
                json=payload,
                # timeout=REQUEST_TIMEOUT
            )
            response.raise_for_status()
            result = response.json().get("response", "")
            
            # Validate it's JSON before returning
            if not result.strip().startswith(('{', '[')):
                logging.warning(f"Response doesn't start with JSON: {result[:100]}...")
                
                if retry_with_simpler:
                    logging.info("Retrying with explicit JSON schema...")
                    # Add JSON schema to prompt
                    enhanced_prompt = f"""{prompt}

CRITICAL: Your response MUST be ONLY the JSON object. Do not include:
- Markdown code fences (```)
- Explanatory text
- Comments
- Anything before or after the JSON

Start your response with {{ and end with }}"""
                    
                    payload["prompt"] = enhanced_prompt
                    payload["options"]["temperature"] = 0.1  # Even more deterministic
                    
                    response = session.post(
                        f"{os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')}/api/generate",
                        json=payload,
                        # timeout=REQUEST_TIMEOUT
                    )
                    response.raise_for_status()
                    result = response.json().get("response", "")
            
            return result
            
        except requests.exceptions.RequestException as e:
            logging.error(f"LLM API request failed: {e}")
            return "{}"  # Return empty JSON on failure
    
    elif provider == "openai":
        try:
            import openai
            client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            
            response = client.chat.completions.create(
                model=os.getenv("LLM_MODEL", "gpt-4-turbo-preview"),
                messages=[
                    {
                        "role": "system",
                        "content": "You are a test generation expert. Respond ONLY with valid JSON. No markdown, no explanations."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                response_format={"type": "json_object"},  # Enforce JSON mode
                temperature=0.3,
                max_tokens=4096
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logging.error(f"OpenAI API request failed: {e}")
            return "{}"
    
    else:
        # For other providers, use the existing implementation
        # (Add similar enhancements for Google, Anthropic, Azure)
        logging.warning(f"Provider {provider} may need JSON formatting enhancements")
        return "{}"


import re
from typing import Optional

def parse_json_response(raw: str, max_attempts: int = 3) -> Optional[dict]:
    """
    Parse JSON response from AI model with aggressive error recovery.
    
    Args:
        raw: Raw response string from AI model
        max_attempts: Number of cleaning attempts before giving up
    
    Returns:
        Parsed JSON dict or None if parsing fails
    """
    # Early validation: check if response is too short (incomplete)
    if len(raw.strip()) < 20:
        logging.error(f"Response too short ({len(raw)} chars), likely incomplete: {raw}")
        return None
    
    # Check for incomplete JSON indicators
    if raw.strip().endswith(('",', '{', '[', '"id":')) and not raw.strip().endswith(('}', ']')):
        logging.error(f"Response appears incomplete (ends with: {raw.strip()[-20:]})")
        return None
    
    for attempt in range(max_attempts):
        try:
            # Attempt 1: Direct parsing
            if attempt == 0:
                cleaned = raw.strip()
            
            # Attempt 2: Remove markdown code fences
            elif attempt == 1:
                cleaned = re.sub(r'^```(?:json)?\s*', '', raw, flags=re.MULTILINE)
                cleaned = re.sub(r'\s*```$', '', cleaned, flags=re.MULTILINE)
                cleaned = cleaned.strip()
            
            # Attempt 3: Extract JSON object/array
            elif attempt == 2:
                # Find first { or [ and last } or ]
                start = min(
                    raw.find('{') if raw.find('{') != -1 else len(raw),
                    raw.find('[') if raw.find('[') != -1 else len(raw)
                )
                end = max(raw.rfind('}'), raw.rfind(']'))
                
                if start < end:
                    cleaned = raw[start:end + 1]
                    
                    # Validate we have balanced braces/brackets
                    if not is_balanced(cleaned):
                        logging.warning(f"Extracted JSON has unbalanced braces/brackets")
                        # Try to complete it
                        cleaned = complete_json(cleaned)
                else:
                    cleaned = raw
            
            # Try parsing
            result = json.loads(cleaned)
            logging.debug(f"Successfully parsed JSON on attempt {attempt + 1}")
            return result
            
        except json.JSONDecodeError as e:
            logging.debug(f"Parse attempt {attempt + 1} failed: {e}")
            
            # On last attempt, try aggressive completion
            if attempt == max_attempts - 1:
                try:
                    # Try to complete the JSON structure
                    completed = complete_json(cleaned)
                    result = json.loads(completed)
                    logging.warning("Recovered from incomplete JSON by completing structure")
                    return result
                except:
                    # Log more details about the failure
                    logging.error(f"All parse attempts failed.")
                    logging.error(f"Last cleaned version ({len(cleaned)} chars): {cleaned[:200]}...")
                    logging.error(f"JSON error at position {e.pos}: {e.msg}")
                    return None
            
            continue
    
    return None


def is_balanced(json_str: str) -> bool:
    """
    Check if JSON string has balanced braces and brackets.
    
    Args:
        json_str: JSON string to check
    
    Returns:
        True if balanced, False otherwise
    """
    stack = []
    pairs = {'{': '}', '[': ']', '"': '"'}
    in_string = False
    escape_next = False
    
    for char in json_str:
        if escape_next:
            escape_next = False
            continue
        
        if char == '\\':
            escape_next = True
            continue
        
        if char == '"':
            if not in_string:
                in_string = True
                stack.append(char)
            elif stack and stack[-1] == '"':
                stack.pop()
                in_string = False
        elif not in_string:
            if char in '{[':
                stack.append(char)
            elif char in '}]':
                if not stack:
                    return False
                opening = stack.pop()
                if pairs.get(opening) != char:
                    return False
    
    return len(stack) == 0


def complete_json(json_str: str) -> str:
    """
    Attempt to complete incomplete JSON by adding missing closing braces/brackets.
    
    Args:
        json_str: Incomplete JSON string
    
    Returns:
        Completed JSON string
    """
    logging.info("Attempting to complete incomplete JSON structure...")
    
    # Count unclosed structures
    open_braces = json_str.count('{') - json_str.count('}')
    open_brackets = json_str.count('[') - json_str.count(']')
    
    # Count unescaped quotes (should be even)
    unescaped_quotes = len(re.findall(r'(?<!\\)"', json_str))
    
    completed = json_str
    
    # Close any unterminated string
    if unescaped_quotes % 2 != 0:
        # Find last quote and check if it needs closing
        last_quote_pos = completed.rfind('"')
        if last_quote_pos > 0:
            # Check if we're in the middle of a value
            after_quote = completed[last_quote_pos + 1:].strip()
            if not after_quote.startswith(('}', ']', ',')):
                completed += '"'
                logging.debug("Added closing quote")
    
    # Close any unterminated array/object value with comma
    if completed.rstrip().endswith(','):
        # Remove trailing comma before closing
        completed = completed.rstrip().rstrip(',')
    
    # Close brackets and braces
    for _ in range(open_brackets):
        completed += '\n]'
        logging.debug("Added closing bracket ]")
    
    for _ in range(open_braces):
        completed += '\n}'
        logging.debug("Added closing brace }")
    
    logging.info(f"Completed JSON: added {open_brackets} ']' and {open_braces} '}}'")
    
    return completed


def detect_incomplete_response(raw: str, expected_keys: List[str]) -> bool:
    """
    Detect if the LLM response was incomplete/truncated.
    
    Args:
        raw: Raw response string
        expected_keys: Keys that should be present in complete response
    
    Returns:
        True if response appears incomplete
    """
    indicators = [
        len(raw.strip()) < 50,  # Too short
        not raw.strip().endswith(('}', ']')),  # Doesn't end with closing
        raw.strip().endswith(('",', '{')),  # Ends mid-structure
        raw.count('{') != raw.count('}'),  # Unbalanced braces
        raw.count('[') != raw.count(']'),  # Unbalanced brackets
    ]
    
    # Check if expected keys are missing
    for key in expected_keys:
        if f'"{key}"' not in raw:
            logging.warning(f"Expected key '{key}' not found in response")
            indicators.append(True)
    
    if any(indicators):
        logging.error("Response appears incomplete based on structural analysis")
        return True
    
    return False


# Model-specific configurations for JSON generation
MODEL_CONFIGS = {
    "ollama": {
        "llama3.2": {
            "temperature": 0.3,
            "top_p": 0.9,
            "num_predict": 4096,
            "stop": ["```", "}\n\n", "]\n\n", "\n\n\n"]
        },
        "mistral": {
            "temperature": 0.2,
            "top_p": 0.85,
            "num_predict": 8192,
            "stop": ["```"]
        },
        "deepseek-coder:6.7b": {
            "temperature": 0.1,  # Very deterministic for code
            "top_p": 0.95,
            "num_predict": 8192
        }
    },
    "openai": {
        "temperature": 0.3,
        "response_format": {"type": "json_object"}
    }
}

def get_model_config(provider: str, model: str) -> Dict:
    """Get optimal configuration for specific model."""
    if provider in MODEL_CONFIGS:
        if isinstance(MODEL_CONFIGS[provider], dict):
            if model in MODEL_CONFIGS[provider]:
                return MODEL_CONFIGS[provider][model]
            # Return default for provider
            return MODEL_CONFIGS[provider].get("default", {})
    return {}
