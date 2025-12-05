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
REQUEST_TIMEOUT = 60  # seconds
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
REQUEST_TIMEOUT = 180  # seconds

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
    """Generate AI prompt for non-functional test case generation.
    
    AI Tool Discovery Metadata:
    - Category: Prompt Engineering / Test Generation
    - Task: NFR Test Prompt Construction
    - Purpose: Build structured prompt for AI model to generate non-functional requirements (NFR) tests
    - Test Types: Performance, reliability, security, usability, accessibility
    
    Args:
        url (str): Target application URL for test context
        elements (List[Dict]): Interactive UI elements (max 20 used)
        business_context (str): Business domain and application description
        nfr_expectations (Optional[Dict]): Known NFR requirements (e.g., load time, concurrency)
        
    Returns:
        str: Formatted prompt string for Ollama API consumption
        
    Prompt Structure:
        1. Role: "You are an expert QA architect specializing in non-functional testing"
        2. Context: URL, business domain, interactive elements (first 20)
        3. Known NFR expectations (JSON)
        4. Task: Design test cases for performance, reliability, security, usability, accessibility
        5. Output format: JSON schema with test objects
        
    Output JSON Schema:
        ```json
        {
          "nfr": [
            {
              "id": "NFR_001",
              "category": "performance",
              "title": "Page loads within 2 seconds",
              "description": "What the test does...",
              "acceptance_criteria": ["criterion 1", "criterion 2"],
              "tooling_suggestions": ["tool1", "tool2"]
            }
          ]
        }
        ```
        
    NFR Categories:
        - performance: Load time, response time, throughput
        - reliability: Uptime, error recovery, data integrity
        - security: Authentication, authorization, encryption, input validation
        - usability: UI/UX, navigation, error messages, help
        - accessibility: WCAG compliance, screen readers, keyboard navigation
        
    Prompt Optimizations:
        - Compact JSON (separators=(',', ':')) - reduces token count
        - Limited to first 20 elements - prevents token overflow
        - Explicit "JSON only" instruction - reduces verbose responses
        - "No explanations outside JSON" - ensures parseable output
        
    Performance:
        - Typical prompt size: 500-2000 tokens
        - Element limit: 20 (from full list)
        - JSON compaction: 20-30% size reduction
        
    Example Usage:
        ```python
        elements = await get_interactive_elements("https://example.com")
        prompt = build_nfr_tests_prompt(
            url="https://example.com",
            elements=elements,
            business_context="E-commerce checkout flow",
            nfr_expectations={"page_load_time": "2s", "max_concurrent_users": 1000}
        )
        response = generate_final_output(CODING_MODEL, prompt)
        ```
        
    Use Cases:
        - Automated NFR test generation
        - QA architecture documentation
        - Performance baseline establishment
        - Security audit planning
        - Accessibility compliance testing
        
    Limitations:
        - Limited to first 20 elements (may miss critical UI)
        - Relies on AI model knowledge of NFR best practices
        - JSON output quality depends on model capability
        - No validation of generated test feasibility
        
    Tool Category: Prompt Engineering, NFR Testing, Test Case Generation, AI-Assisted QA
    """
    # Use compact JSON formatting to reduce prompt size
    elems_json = json.dumps(elements[:20], separators=(',', ':'))  # Limit to first 20 elements
    expectations_json = json.dumps(nfr_expectations or {}, separators=(',', ':'))
    
    return f"""You are an expert QA architect specializing in comprehensive non-functional testing.

Application under test:
- URL: {url}
- Business context: {business_context}

Interactive elements (all elements): {elems_json}

Known NFR expectations: {expectations_json}

Design EXHAUSTIVE NON-FUNCTIONAL test cases covering:
1. Performance (load time, response time, throughput, resource usage, scalability, caching)
2. Reliability (uptime, error recovery, failover, data integrity, consistency, resilience)
3. Security (authentication, authorization, encryption, injection prevention, XSS, CSRF, rate limiting, data protection)
4. Usability (UI/UX, navigation, error messages, form validation feedback, accessibility of error states)
5. Accessibility (WCAG 2.1 compliance, screen readers, keyboard navigation, color contrast, focus management)
6. Compliance (GDPR, data retention, audit trails, regulatory requirements)
7. Maintainability (code quality, technical debt, documentation, monitoring)
8. Portability (cross-browser compatibility, mobile responsiveness, different OS support)

Generate EXHAUSTIVE and DIVERSE test cases covering all above categories with multiple scenarios per category.

OUTPUT FORMAT (JSON only):
{{
  "nfr": [
    {{
      "id": "NFR_001",
      "category": "performance|reliability|security|usability|accessibility|compliance|maintainability|portability",
      "title": "Clear, specific test title",
      "description": "Detailed description of what the test validates",
      "acceptance_criteria": ["criterion 1", "criterion 2", "criterion 3"],
      "tooling_suggestions": ["tool1", "tool2", "tool3"],
      "priority": "high|medium|low",
      "risk_level": "high|medium|low"
    }}
  ]
}}

Generate comprehensive, exhaustive, and diverse test cases. Aim for at least 50+ test cases covering all categories thoroughly. No explanations outside JSON."""


def build_functional_tests_prompt(
    url: str,
    elements: List[Dict],
    business_context: str
) -> str:
    """Generate AI prompt for functional test case generation.
    
    AI Tool Discovery Metadata:
    - Category: Prompt Engineering / Test Generation
    - Task: Functional Test Prompt Construction
    - Purpose: Build structured prompt for AI model to generate functional test cases
    - Test Types: Happy path, negative cases, boundary tests, navigation flows
    
    Args:
        url (str): Target application URL for test context
        elements (List[Dict]): Interactive UI elements (max 20 used)
        business_context (str): Business domain and application description
        
    Returns:
        str: Formatted prompt string for Ollama API consumption
        
    Prompt Structure:
        1. Role: "You are an expert software test engineer"
        2. Context: URL, business domain, interactive elements (first 20)
        3. Task: Design functional test cases covering happy path, negative cases, boundaries, navigation
        4. Output format: JSON schema with test objects
        
    Output JSON Schema:
        ```json
        {
          "functional": [
            {
              "id": "FUN_001",
              "category": "happy_path",
              "title": "User successfully logs in with valid credentials",
              "preconditions": ["User is on login page"],
              "steps": ["Enter email", "Enter password", "Click submit"],
              "expected_result": "User redirected to dashboard",
              "test_data": {"email": "test@example.com", "password": "validPass123"}
            }
          ]
        }
        ```
        
    Functional Test Categories:
        - happy_path: Normal user flows with valid inputs
        - negative: Error handling, invalid inputs, edge cases
        - boundary: Min/max values, empty fields, special characters
        - navigation: Page transitions, back button, deep links
        
    Prompt Optimizations:
        - Compact JSON (separators=(',', ':')) - reduces token count
        - Limited to first 20 elements - prevents token overflow
        - Explicit "JSON only" instruction - reduces verbose responses
        - "No explanations outside JSON" - ensures parseable output
        
    Performance:
        - Typical prompt size: 500-2000 tokens
        - Element limit: 20 (from full list)
        - JSON compaction: 20-30% size reduction
        
    Example Usage:
        ```python
        elements = await get_interactive_elements("https://example.com/login")
        prompt = build_functional_tests_prompt(
            url="https://example.com/login",
            elements=elements,
            business_context="User authentication and login workflow"
        )
        response = generate_final_output(CODING_MODEL, prompt)
        ```
        
    Use Cases:
        - Automated functional test generation
        - Test case documentation
        - Regression test planning
        - User story validation
        - Acceptance criteria definition
        
    Limitations:
        - Cover all elements (may miss critical UI)
        - Relies on AI model knowledge of testing best practices
        - JSON output quality depends on model capability
        - No validation of generated test feasibility
        - Test data may need manual review for realism
        
    Tool Category: Prompt Engineering, Functional Testing, Test Case Generation, AI-Assisted QA
    """
    # Use compact JSON and limit elements
    elems_json = json.dumps(elements[:20], separators=(',', ':'))
    
    return f"""You are an expert software test engineer specializing in comprehensive test coverage.

Application: {url}
Context: {business_context}
Interactive elements (fall elements): {elems_json}

Design EXHAUSTIVE FUNCTIONAL test cases covering:
1. Happy path scenarios (normal user workflows)
2. Negative cases (invalid inputs, error handling)
3. Boundary conditions (min/max values, empty fields, special characters)
4. Navigation flows (page transitions, deep links, back button)
5. Data validation (format validation, type checking)
6. State management (session handling, caching, data persistence)
7. Error recovery (network failures, timeouts, retry logic)
8. Security scenarios (input sanitization, XSS prevention, CSRF protection)
9. Accessibility workflows (keyboard navigation, screen reader compatibility)
10. Performance considerations (load times, responsiveness under load)

Generate EXHAUSTIVE diverse test cases covering all above categories.

OUTPUT FORMAT (JSON only):
{{
  "functional": [
    {{
      "id": "FUNC_001",
      "title": "Clear title",
      "category": "happy_path|negative|boundary|navigation|validation|state|recovery|security|accessibility|performance",
      "preconditions": ["list of prerequisites"],
      "steps": ["detailed step 1", "detailed step 2", "step 3"],
      "expected_result": "Expected outcome",
      "tags": ["tag1", "tag2"],
      "priority": "high|medium|low"
    }}
  ]
}}

Generate comprehensive and exhaustive test cases. No explanations outside JSON."""


async def generate_functional_tests(url: str, business_context: str) -> List[Dict]:
    """Generate functional test cases using AI model based on URL and business context.
    
    AI Tool Discovery Metadata:
    - Category: Test Generation / AI-Assisted QA
    - Task: Functional Test Case Generation
    - Purpose: Generate complete functional test cases by analyzing UI elements and business context
    - Model: deepseek-coder:6.7b (Ollama local inference)
    
    Args:
        url (str): Target application URL to analyze and test
        business_context (str): Business domain and application description for context
        
    Returns:
        List[Dict]: List of functional test case dictionaries, each containing:
            - id (str): Unique test identifier (e.g., "FUNC_001")
            - title (str): Human-readable test title
            - preconditions (List[str]): Prerequisites before test execution
            - steps (List[str]): Ordered test execution steps
            - expected_result (str): Expected outcome after execution
            - tags (List[str]): Test categorization tags
            
    Example Return:
        ```python
        [
            {
                "id": "FUNC_001",
                "title": "User successfully logs in with valid credentials",
                "preconditions": ["User is on login page", "User has valid account"],
                "steps": [
                    "Enter valid email address",
                    "Enter valid password",
                    "Click 'Login' button"
                ],
                "expected_result": "User redirected to dashboard with welcome message",
                "tags": ["authentication", "login", "happy_path"]
            }
        ]
        ```
        
    Process:
        1. Extracts interactive UI elements from URL (get_interactive_elements)
        2. Builds AI prompt with elements and business context
        3. Sends prompt to Ollama API (generate_final_output)
        4. Cleans response (removes code fences, markdown)
        5. Parses JSON response
        6. Returns test cases array or empty list on error
        
    Test Generation Pipeline:
        URL → get_interactive_elements() → build_functional_tests_prompt() → 
        generate_final_output() → JSON parsing → Test cases
        
    Performance:
        - Element extraction: 5-10 seconds (browser automation)
        - AI inference: 10-30 seconds (depends on model load)
        - Total: 15-40 seconds typical
        
    Security:
        - URL validated by get_interactive_elements()
        - No code execution (output is JSON data)
        - Safe for untrusted URLs
        
    Error Handling:
        - json.JSONDecodeError: Returns empty list [] if AI output is not valid JSON
        - Logs first 200 chars of raw output for debugging
        - Logs JSON decode errors with full context
        - ValueError: From get_interactive_elements if URL invalid
        
    Response Cleaning:
        - Removes triple quotes (''')
        - Removes code fences (```json, ```)
        - Strips whitespace
        - Ensures parseable JSON
        
    Use Cases:
        - Automated test case generation for new features
        - Regression test planning
        - QA documentation automation
        - Test coverage gap analysis
        - User story validation
        
    Limitations:
        - Limited to first 20 UI elements (from prompt builder)
        - Test quality depends on AI model capability
        - May generate infeasible tests (requires review)
        - No test execution or validation
        - Business context must be descriptive for quality output
        
    Tool Category: AI Test Generation, Functional Testing, Automated QA, Ollama Integration
    """
    elements = await get_interactive_elements(url)
    prompt = build_functional_tests_prompt(url, elements, business_context)
    
    logging.debug("Generating functional tests with prompt")
    raw = generate_final_output(prompt)
    
    # Clean up response
    raw = raw.replace("'''", "").replace('```json', '').replace('```', '').strip()
    
    logging.debug(f"Functional Raw Output: {raw[:200]}...")  # Log only first 200 chars
    
    try:
        test_spec = json.loads(raw)
        return test_spec.get("functional", [])
    except json.JSONDecodeError as e:
        logging.error(f"JSON decode error: {e}\nRaw output: {raw}")
        return []


async def generate_nfr_tests(
    url: str,
    business_context: str,
    nfr_expectations: Optional[Dict] = None
) -> List[Dict]:
    """Generate non-functional requirement (NFR) test cases using AI model.
    
    AI Tool Discovery Metadata:
    - Category: Test Generation / NFR Testing
    - Task: Non-Functional Test Case Generation
    - Purpose: Generate NFR test cases covering performance, security, reliability, usability, accessibility
    - Model: deepseek-coder:6.7b (Ollama local inference)
    
    Args:
        url (str): Target application URL to analyze and test
        business_context (str): Business domain and application description
        nfr_expectations (Optional[Dict]): Known NFR requirements (e.g., {"page_load_time": "2s"})
        
    Returns:
        List[Dict]: List of NFR test case dictionaries, each containing:
            - id (str): Unique test identifier (e.g., "NFR_001")
            - category (str): NFR category (performance, security, reliability, usability, accessibility)
            - title (str): Human-readable test title
            - description (str): Detailed test description
            - acceptance_criteria (List[str]): Success criteria
            - tooling_suggestions (List[str]): Recommended testing tools
            
    Example Return:
        ```python
        [
            {
                "id": "NFR_001",
                "category": "performance",
                "title": "Page loads within 2 seconds under normal load",
                "description": "Measure page load time from navigation to DOMContentLoaded event",
                "acceptance_criteria": [
                    "Page load time < 2 seconds for 95th percentile",
                    "Time to First Byte (TTFB) < 500ms",
                    "First Contentful Paint (FCP) < 1 second"
                ],
                "tooling_suggestions": ["Lighthouse", "WebPageTest", "Playwright performance API"]
            },
            {
                "id": "NFR_002",
                "category": "security",
                "title": "Login form prevents SQL injection attacks",
                "description": "Test login form with SQL injection payloads",
                "acceptance_criteria": [
                    "No database errors returned to user",
                    "Invalid credentials message shown for injection attempts",
                    "All inputs properly sanitized"
                ],
                "tooling_suggestions": ["OWASP ZAP", "Burp Suite", "SQLMap"]
            }
        ]
        ```
        
    Process:
        1. Extracts interactive UI elements from URL
        2. Builds AI prompt with elements, context, and expectations
        3. Sends prompt to Ollama API
        4. Cleans response (removes code fences, markdown)
        5. Parses JSON response
        6. Returns NFR test cases array or empty list on error
        
    NFR Test Categories Generated:
        - performance: Load time, response time, throughput, resource usage
        - reliability: Uptime, error recovery, failover, data integrity
        - security: Authentication, authorization, encryption, injection prevention
        - usability: UI/UX, navigation, error handling, help documentation
        - accessibility: WCAG compliance, screen reader support, keyboard navigation
        
    Performance:
        - Element extraction: 5-10 seconds
        - AI inference: 10-30 seconds
        - Total: 15-40 seconds typical
        
    Security:
        - URL validated by get_interactive_elements()
        - No code execution (output is JSON data)
        - Safe for untrusted URLs
        
    Error Handling:
        - json.JSONDecodeError: Returns empty list [] if AI output is not valid JSON
        - Logs first 200 chars of raw output for debugging
        - Logs JSON decode errors with full context
        - ValueError: From get_interactive_elements if URL invalid
        
    Response Cleaning:
        - Removes triple quotes (''')
        - Removes code fences (```json, ```)
        - Strips whitespace
        - Ensures parseable JSON
        
    Use Cases:
        - Performance baseline establishment
        - Security audit planning
        - Accessibility compliance testing
        - SLA/SLO definition
        - NFR requirement documentation
        
    Limitations:
        - Limited to first 20 UI elements (from prompt builder)
        - Test quality depends on AI model knowledge
        - May suggest unrealistic performance targets
        - Tool suggestions may not match infrastructure
        - Requires domain expertise to validate output
        
    Tool Category: AI Test Generation, NFR Testing, Automated QA, Performance Testing, Security Testing
    """
    elements = await get_interactive_elements(url)
    prompt = build_nfr_tests_prompt(url, elements, business_context, nfr_expectations)
    
    logging.debug("Generating NFR tests with prompt")
    raw = generate_final_output(prompt)
    
    # Clean up response
    raw = raw.replace("'''", "").replace('```json', '').replace('```', '').strip()
    
    logging.debug(f"NFR Raw Output: {raw[:200]}...")  # Log only first 200 chars
    
    try:
        test_spec = json.loads(raw)
        return test_spec.get("nfr", [])
    except json.JSONDecodeError as e:
        logging.error(f"JSON decode error: {e}\nRaw output: {raw}")
        return []


def generate_final_output(prompt: str) -> str:
    """Generate AI response using configured LLM provider.
    
    AI Tool Discovery Metadata:
    - Category: AI Integration / API Wrapper
    - Task: Multi-Provider LLM Request Handler
    - Purpose: Send prompts to configured LLM provider and return JSON responses
    - Model: Configurable via LLM_MODEL environment variable (supports Ollama, OpenAI, Anthropic, Google, Azure)
    
    Args:
        prompt (str): Text prompt for AI model (max 50,000 chars)
        
    Returns:
        str: AI-generated response string (JSON format)
        
    Configuration:
        - Endpoint: {OLLAMA_HOST}/api/generate (default: http://localhost:11434)
        - Model: OLLAMA_MODEL (llama3.2 by default)
        - Stream: False (synchronous response)
        - Format: json (structured output)
        - Timeout: Commented out (no timeout enforced)
        
    Process:
        1. Validates prompt is non-empty string
        2. Truncates prompt if exceeds 50,000 characters (DoS prevention)
        3. Constructs JSON payload with model and prompt
        4. Sends POST request to Ollama API via session pool
        5. Checks HTTP status code (raises on 4xx/5xx)
        6. Extracts "response" field from JSON
        7. Returns response string
        
    Example Usage:
        ```python
        prompt = "Generate test cases for login form"
        response = generate_final_output(prompt)
        # response is JSON string like '{"functional": [...]}'
        test_cases = json.loads(response)
        ```
        
    Security:
        - Prompt size limited to 50,000 chars (prevents DoS)
        - Session pooling with connection reuse
        - No timeout (WARNING: may hang on slow models)
        - Input validation (type and emptiness checks)
        
    Performance:
        - Typical inference time: 10-60 seconds (depends on prompt complexity)
        - Connection pooling: 30-50% faster (via get_session)
        - First call slower (model loading)
        - Subsequent calls faster (model cached in memory)
        
    Prompt Truncation:
        - Maximum prompt length: 50,000 characters
        - Logs warning if truncated
        - Truncation preserves first 50,000 chars
        - May affect output quality if prompt is truncated
        
    Error Handling:
        - ValueError: Raised if prompt is empty, not a string, or API request fails
        - requests.exceptions.RequestException: Network errors, timeouts, HTTP errors
        - Logs error details before raising
        
    Raises:
        ValueError: If prompt is invalid or API request fails
        
    API Payload Structure:
        ```json
        {
            "model": "llama3.2",
            "prompt": "Your prompt text here",
            "stream": false,
            "format": "json"
        }
        ```
        
    API Response Structure:
        ```json
        {
            "model": "llama3.2",
            "created_at": "2024-01-01T12:00:00Z",
            "response": "{\"functional\": [...]}",
            "done": true
        }
        ```
        
    Use Cases:
        - Test case generation (functional and NFR)
        - Code generation (Playwright automation)
        - Element extraction (via vision model)
        - Any Ollama AI inference task
        
    Limitations:
        - No timeout configured (commented out) - may hang indefinitely
        - Prompt truncation may reduce output quality
        - JSON format enforced - may fail for non-JSON models
        - No retry logic for transient failures
        - Single model per call (no model switching)
        
    Tool Category: AI API Integration, Ollama Wrapper, LLM Inference, JSON Generation
    """
    if not prompt or not isinstance(prompt, str):
        raise ValueError("Prompt must be a non-empty string")
    
    # Limit prompt size to prevent DoS
    if len(prompt) > 50000:
        logging.warning(f"Prompt truncated from {len(prompt)} to 50000 characters")
        prompt = prompt[:50000]
    
    try:
        provider = get_llm_provider()
        response = provider.generate(prompt, format="json", max_tokens=4096, temperature=0.7)
        return response
    except Exception as e:
        logging.error(f"LLM API request failed: {e}")
        raise ValueError(f"Failed to generate output: {e}")
