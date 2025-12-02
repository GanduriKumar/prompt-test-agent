from playwright.sync_api import sync_playwright
import logging

logging.basicConfig(
    level=logging.DEBUG,  # Show DEBUG and above
    format="%(asctime)s - %(levelname)s - %(message)s",
    force=True  # Override any previous logging config
)
#Viewport size for the browser window
VIEWPORT= {'width': 1280, 'height': 720}

def open_browser(url: str) -> None:
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
    with sync_playwright() as p:
        # Launch a Chromium browser instance (not in headless mode)
        browser = p.chromium.launch(headless=False)
        # Create a new page in the browser
        page = browser.new_page()
        #set the viewport size
        page.set_viewport_size(VIEWPORT)
        # Navigate to the specified URL
        page.goto(url)
        # Wait for the page to fully load
        page.wait_for_load_state('load')
        # log the title of the loaded page
        logging.info(f"Title of the page: {page.title()}")
        # Close the browser after use
        browser.close()

def open_browser_capture_screen(url: str, screenshot_path: str) -> None:
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
    with sync_playwright() as p:
        # Launch a Chromium browser instance (not in headless mode)
        browser = p.chromium.launch(headless=False)
        # Create a new page in the browser
        page = browser.new_page()
        #set the viewport size
        page.set_viewport_size(VIEWPORT)
        # Navigate to the specified URL
        page.goto(url)
        # Wait for the page to fully load
        page.wait_for_load_state('load')
        page.screenshot(path=screenshot_path, full_page=True) 
        return browser, page  

        # browser.close()