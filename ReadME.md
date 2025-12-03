# Prompt Test Agent

A Python-based web automation and testing framework that combines Playwright browser automation with Ollama AI models for intelligent screenshot analysis and UI testing.

## Overview

This project provides tools for automated web testing and analysis using:
- **Playwright** for browser automation and screenshot capture
- **Ollama** for AI-powered visual analysis and test instruction processing
- **Computer Use Agent (CUA)** pattern for multimodal testing workflows

## Features

- 🌐 Automated browser control with Chromium
- 📸 Full-page screenshot capture with configurable viewport (1280x720)
- 🤖 AI-powered visual analysis using local Ollama models
- 🔍 Intelligent HTML element detection and testing
- 📝 Natural language test instructions
- 🎯 Non-headless browser mode for visual debugging
- 🔐 Environment-based configuration management
- 📊 Comprehensive debug logging

## Project Structure

```
.
├── cua_client.py           # Core CUA request handler and Ollama integration
├── cua_query.py            # Main entry point for testing workflows
├── open_browser.py         # Playwright browser automation utilities
├── requirements.txt        # Python dependencies
├── LICENSE                 # MIT License
├── ReadME.md              # Project documentation
├── .env                   # Environment configuration (not tracked)
├── .gitignore            # Git ignore rules
├── __pycache__/          # Python bytecode cache (not tracked)
└── .idea/                # PyCharm IDE configuration
    ├── .gitignore
    ├── misc.xml
    ├── modules.xml
    ├── prompt-test-agent.iml
    ├── vcs.xml
    ├── workspace.xml
    └── inspectionProfiles/
```

## Prerequisites

- Python 3.8 or higher
- [Ollama](https://ollama.ai/) installed and running locally
- Chromium browser (installed via Playwright)
- Windows OS (for `python-certifi-win32` support, optional for other platforms)

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/KumarGN/prompt-test-agent.git
   cd prompt-test-agent
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install Playwright browsers:**
   ```bash
   playwright install chromium
   ```

4. **Configure environment variables:**
   Create a `.env` file in the project root:
   ```env
   OLLAMA_MODEL=your-model-name
   ```
   Example models: `llama2`, `mistral`, `llava`, or any vision-capable model

5. **Verify Ollama is running:**
   ```bash
   ollama serve
   ```

## Usage

### Interactive Testing Mode

Run the main query script for interactive web testing:

```bash
python cua_query.py
```

**Workflow:**
1. Enter the URL you want to test when prompted
2. The browser will open and navigate to the URL
3. A full-page screenshot is captured as `screenshot.png`
4. The AI analyzes the screenshot based on configured instructions
5. Results are logged and displayed in the console

### Programmatic Usage

#### Example 1: Capture Screenshot and Get Browser Handles

```python
from open_browser import open_browser_capture_screen

# Capture screenshot and get live browser/page objects
browser, page = open_browser_capture_screen(
    url="https://example.com",
    screenshot_path="output/screenshot.png"
)

# Perform additional interactions with the page
# page.click("button#submit")
# page.fill("input[name='username']", "testuser")

# Important: Close browser when done
browser.close()
```

#### Example 2: Simple Browser Navigation

```python
from open_browser import open_browser

# Opens browser, navigates to URL, logs title, then closes
open_browser("https://example.com")
```

#### Example 3: AI-Powered Screenshot Analysis

```python
from cua_client import create_cua_request

# Analyze screenshot with custom instructions
result = create_cua_request(
    instructions="List all HTML input tags in the webpage",
    screenshot_path="screenshot.png"
)

print(result)
```

#### Example 4: Multi-Step Testing Workflow

```python
from open_browser import open_browser_capture_screen
from cua_client import create_cua_request
import logging

# Step 1: Capture initial state
browser, page = open_browser_capture_screen(
    "https://example.com/form",
    "step1_initial.png"
)

# Step 2: Analyze initial form
analysis = create_cua_request(
    "Identify all required form fields",
    "step1_initial.png"
)
logging.info(f"Initial form analysis: {analysis}")

# Step 3: Interact with the page
page.fill("input[name='email']", "test@example.com")
page.screenshot(path="step2_filled.png", full_page=True)

# Step 4: Validate filled form
validation = create_cua_request(
    "Verify that the email field is correctly filled",
    "step2_filled.png"
)
logging.info(f"Validation result: {validation}")

# Clean up
browser.close()
```

## Key Components

### [`open_browser.py`](open_browser.py)

Browser automation utilities with Playwright:

#### [`open_browser(url)`](open_browser.py)
- Launches Chromium in non-headless mode
- Navigates to specified URL
- Waits for page load
- Logs page title
- Automatically closes browser

#### [`open_browser_capture_screen(url, screenshot_path)`](open_browser.py)
- Launches Chromium with viewport configuration (1280x720)
- Navigates to URL and waits for load
- Captures full-page screenshot
- **Returns live browser and page objects** for further interaction
- **Important:** Caller must close browser manually

**Viewport Configuration:**
```python
VIEWPORT = {'width': 1280, 'height': 720}
```

### [`cua_client.py`](cua_client.py)

AI integration layer for Ollama:

#### [`encode_file_to_base64(screenshot_path)`](cua_client.py)
- Encodes image files to base64 data URIs
- Returns formatted string: `data:image/png;base64,{encoded_data}`
- Includes debug logging for encoding process

#### [`create_cua_request(instructions, screenshot_path)`](cua_client.py)
- Main CUA request handler for AI analysis
- Constructs multimodal chat requests (text + image)
- Sends requests to configured Ollama model
- Returns AI-generated analysis/response
- Supports both text-only and multimodal requests
- Includes comprehensive logging
- 30-second timeout for API calls

**Request Structure:**
```python
content = [
    {"type": "text", "text": instructions},
    {"type": "input_image", "image": {"src": base64_data, "alt": "screenshot"}}
]
```

### [`cua_query.py`](cua_query.py)

Main application orchestrator:

**Workflow Steps:**
1. Loads environment variables from `.env` file
2. Prompts user for target URL
3. Captures screenshot via [`open_browser_capture_screen`](open_browser.py)
4. Validates screenshot file existence
5. Sends analysis request via [`create_cua_request`](cua_client.py)
6. Logs results at each step

**Default Test Instructions:**
```python
test_instructions = "List all the HTML inputs tags in the webpage"
```

**Output File:**
- Screenshots saved as `screenshot.png` in project root

## Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| playwright | ~1.56.0 | Browser automation and testing framework |
| ollama | ~0.6.1 | Local AI model integration and chat API |
| python-dotenv | ~1.2.1 | Environment variable management from `.env` files |
| certifi | ~2025.11.12 | SSL certificate validation bundle |
| python-certifi-win32 | ~1.6.1 | Windows-specific SSL certificate support |

See [`requirements.txt`](requirements.txt) for exact versions.

## Configuration

### Environment Variables

Configure in `.env` file (not tracked in version control):

```env
# Required: Ollama model name
# Examples: llama2, mistral, llava, bakllava
OLLAMA_MODEL=llava
```

**Supported Model Types:**
- Text-only models (for text-based analysis)
- Vision-capable models (for screenshot analysis)
- Multimodal models recommended: `llava`, `bakllava`

### Logging Configuration

All modules use consistent DEBUG-level logging:

```python
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    force=True
)
```

**Logged Events:**
- URL navigation
- Screenshot capture
- File encoding
- Ollama API requests/responses
- File validation
- Error conditions

### Viewport Settings

Standardized browser viewport in [`open_browser.py`](open_browser.py):

```python
VIEWPORT = {'width': 1280, 'height': 720}
```

Modify this constant to change screenshot dimensions.

## AI Agent Discovery

This framework is designed for AI agent discoverability and automation:

**Tags:** `#testing` `#screenshot-analysis` `#ui-automation` `#multimodal` `#ollama` `#cua-agent` `#web-automation` `#playwright` `#computer-use-agent`

**Supported AI Tasks:**
- Visual regression testing
- HTML element detection and validation
- UI interaction verification
- Accessibility testing
- Form field analysis
- Cross-browser compatibility checks
- Natural language test case execution

## Use Cases & Examples

### Use Case 1: Form Validation Testing

```python
from cua_client import create_cua_request
from open_browser import open_browser_capture_screen

# Capture login form
browser, page = open_browser_capture_screen(
    "https://example.com/login",
    "login_page.png"
)

# Analyze form elements
result = create_cua_request(
    "List all form input fields and validate required attributes",
    "login_page.png"
)

print(result)
browser.close()
```

### Use Case 2: Accessibility Audit

```python
result = create_cua_request(
    "Check for accessibility issues: missing alt text, contrast ratios, ARIA labels",
    "page_screenshot.png"
)
```

### Use Case 3: Element Extraction

```python
# Extract specific elements
result = create_cua_request(
    "List all buttons with their text content and IDs",
    "screenshot.png"
)
```

### Use Case 4: Visual Comparison

```python
# Capture before state
browser, page = open_browser_capture_screen(
    "https://example.com",
    "before.png"
)

# Make changes
page.click("#toggle-button")
page.screenshot(path="after.png", full_page=True)

# Compare states
result = create_cua_request(
    "Compare these two screenshots and describe the differences",
    "after.png"  # Note: Multi-image comparison requires custom implementation
)

browser.close()
```

## Troubleshooting

### Common Issues

#### 1. **Ollama Connection Errors**
```
Error: connection refused
```
**Solution:**
- Ensure Ollama is running: `ollama serve`
- Verify model is downloaded: `ollama list`
- Check model name in `.env` matches installed model

#### 2. **Playwright Browser Not Found**
```
Error: Executable doesn't exist
```
**Solution:**
```bash
playwright install chromium
```

#### 3. **Screenshot File Not Found**
```
FileNotFoundError: [Errno 2] No such file or directory: 'screenshot.png'
```
**Solution:**
- Check write permissions in current directory
- Verify `screenshot_path` is correct
- Ensure parent directories exist

#### 4. **SSL Certificate Errors (Windows)**
```
SSLError: certificate verify failed
```
**Solution:**
- Ensure `python-certifi-win32` is installed
- Update certifi: `pip install --upgrade certifi`

#### 5. **Model Response Timeout**
```
TimeoutError: Request exceeded 30 seconds
```
**Solution:**
- Increase timeout in [`cua_client.py`](cua_client.py):
```python
response = ollama.chat(
    model=os.getenv("OLLAMA_MODEL"),
    messages=[...],
    options={"timeout": 60}  # Increase to 60 seconds
)
```

#### 6. **Browser Won't Close**
**Solution:**
- Manually call `browser.close()` when using [`open_browser_capture_screen`](open_browser.py)
- The function returns live handles; you must close them explicitly

### Debug Mode

Enable verbose logging by ensuring `level=logging.DEBUG` in all modules (already configured).

## Project Files

### Core Modules
- [`cua_query.py`](cua_query.py) - Main application entry point
- [`cua_client.py`](cua_client.py) - Ollama AI client and CUA request handler
- [`open_browser.py`](open_browser.py) - Playwright browser automation

### Configuration
- [`.env`](.env) - Environment variables (not tracked)
- [`requirements.txt`](requirements.txt) - Python dependencies
- [`.gitignore`](.gitignore) - Git ignore patterns

### Documentation & Legal
- [`LICENSE`](LICENSE) - MIT License
- [`ReadME.md`](ReadME.md) - This file

### IDE Configuration
- `.idea/` - PyCharm project settings (partially tracked)

## Development Setup

### For Contributors

1. **Fork and clone** the repository
2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   playwright install chromium
   ```
4. **Configure `.env`** with your Ollama model
5. **Test installation:**
   ```bash
   python cua_query.py
   ```

### Running Tests

Currently, the project uses manual testing via [`cua_query.py`](cua_query.py). Future versions may include automated test suites.

## Roadmap

- [ ] Add unit tests for core functions
- [ ] Support for multiple browser engines (Firefox, WebKit)
- [ ] Batch screenshot processing
- [ ] Multi-image comparison capabilities
- [ ] Custom viewport configurations via CLI
- [ ] Export results to JSON/CSV
- [ ] Web UI for test management
- [ ] Docker containerization
- [ ] CI/CD integration examples

## Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Code Style
- Follow PEP 8 guidelines
- Include docstrings for all functions
- Add logging statements for key operations
- Update this README for new features

## License

This project is licensed under the MIT License - see the [`LICENSE`](LICENSE) file for details.

**Copyright (c) 2025 KumarGN**

## Author

**KumarGN**
- GitHub: [@KumarGN](https://github.com/KumarGN)

## Acknowledgments

- Built with [Playwright](https://playwright.dev/) for reliable browser automation
- Powered by [Ollama](https://ollama.ai/) for local AI model inference
- Inspired by Computer Use Agent (CUA) patterns and multimodal AI workflows
- Uses [python-dotenv](https://github.com/theskumar/python-dotenv) for configuration management

## Technical Notes

### Architecture
- **Modular Design:** Separation of concerns between browser automation, AI integration, and orchestration
- **Non-Headless Mode:** Visual debugging enabled by default for transparency
- **Synchronous API:** Uses Playwright's sync API for simplicity
- **Base64 Encoding:** Screenshots encoded for Ollama API compatibility

### Performance Considerations
- Screenshots are saved to disk (not held in memory)
- Full-page screenshots may be large for long pages
- Ollama API calls have 30-second default timeout
- Browser instances must be manually closed to free resources

### Security Considerations
- `.env` file not tracked in version control (contains sensitive configuration)
- Local Ollama instance (no external API calls by default)
- Screenshots may contain sensitive information (handle carefully)

---

**Note:** This is an active development project. APIs and functionality may change. Please check the repository for the latest updates.

**Last Updated:** 2025-12-03