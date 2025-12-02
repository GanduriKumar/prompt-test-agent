# Prompt Test Agent

A Python-based web automation and testing framework that combines Playwright browser automation with Ollama AI models for intelligent screenshot analysis and UI testing.

## Overview

This project provides tools for automated web testing and analysis using:
- **Playwright** for browser automation and screenshot capture
- **Ollama** for AI-powered visual analysis and test instruction processing
- **Computer Use Agent (CUA)** pattern for multimodal testing workflows

## Features

- 🌐 Automated browser control with Chromium
- 📸 Full-page screenshot capture
- 🤖 AI-powered visual analysis using local Ollama models
- 🔍 Intelligent HTML element detection and testing
- 📝 Natural language test instructions
- 🎯 Non-headless browser mode for visual debugging

## Project Structure

```
.
├── cua_client.py           # Core CUA request handler and Ollama integration
├── cua_query.py            # Main entry point for testing workflows
├── open_browser.py         # Playwright browser automation utilities
├── requirements.txt        # Python dependencies
├── .env                    # Environment configuration (not tracked)
├── .gitignore             # Git ignore rules
└── LICENSE                # MIT License
```

## Prerequisites

- Python 3.8 or higher
- [Ollama](https://ollama.ai/) installed and running locally
- Chromium browser (installed via Playwright)

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

## Usage

### Basic Web Testing

Run the interactive test query:

```bash
python cua_query.py
```

You'll be prompted to:
1. Enter a URL to test
2. The script will capture a screenshot
3. AI analysis will be performed based on the configured instructions

### Programmatic Usage

#### Open Browser and Capture Screenshot

```python
from open_browser import open_browser_capture_screen

# Capture screenshot and get browser handles
browser, page = open_browser_capture_screen(
    url="https://example.com",
    screenshot_path="output/screenshot.png"
)

# Perform additional interactions
# ...

browser.close()
```

#### Create AI-Powered Test Request

```python
from cua_client import create_cua_request

# Analyze screenshot with AI
result = create_cua_request(
    instructions="List all HTML input tags in the webpage",
    screenshot_path="screenshot.png"
)

print(result)
```

## Key Components

### [`open_browser.py`](open_browser.py)

Browser automation utilities:
- [`open_browser(url)`](open_browser.py) - Simple browser launch and navigation
- [`open_browser_capture_screen(url, screenshot_path)`](open_browser.py) - Browser launch with screenshot capture

**Viewport Configuration:**
```python
VIEWPORT = {'width': 1280, 'height': 720}
```

### [`cua_client.py`](cua_client.py)

AI integration layer:
- [`encode_file_to_base64(screenshot_path)`](cua_client.py) - Image encoding for API requests
- [`create_cua_request(instructions, screenshot_path)`](cua_client.py) - Main CUA request handler

Supports multimodal requests with:
- Text instructions (natural language)
- Image context (screenshots)

### [`cua_query.py`](cua_query.py)

Main application entry point that orchestrates:
1. User input for target URL
2. Screenshot capture via Playwright
3. AI analysis via Ollama
4. Result logging and display

## Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| playwright | ~1.56.0 | Browser automation and testing |
| ollama | ~0.6.1 | Local AI model integration |
| python-dotenv | ~1.2.1 | Environment variable management |
| certifi | ~2025.11.12 | SSL certificate validation |
| python-certifi-win32 | ~1.6.1 | Windows SSL support |

See [`requirements.txt`](requirements.txt) for complete dependency list.

## Configuration

### Environment Variables

Configure in `.env` file:

```env
# Required: Ollama model name (e.g., llama2, mistral, etc.)
OLLAMA_MODEL=your-model-name
```

### Logging

All modules use Python's standard logging with DEBUG level:
```python
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    force=True
)
```

## AI Agent Discovery

This framework is designed for AI agent discoverability and automation:

**Tags:** `#testing` `#screenshot-analysis` `#ui-automation` `#multimodal` `#ollama` `#cua-agent` `#web-automation` `#playwright`

**Supported Tasks:**
- Visual regression testing
- HTML element detection and validation
- UI interaction verification
- Accessibility testing
- Cross-browser compatibility checks

## Examples

### Example 1: Form Validation Testing

```python
from cua_client import create_cua_request
from open_browser import open_browser_capture_screen

# Capture login page
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

### Example 2: Accessibility Audit

```python
result = create_cua_request(
    "Check for accessibility issues: missing alt text, contrast ratios, ARIA labels",
    "page_screenshot.png"
)
```

## Troubleshooting

### Common Issues

1. **Ollama connection errors:**
   - Ensure Ollama is running: `ollama serve`
   - Verify model is downloaded: `ollama list`

2. **Playwright browser not found:**
   - Run: `playwright install chromium`

3. **Screenshot file not found:**
   - Check file permissions
   - Verify screenshot_path is absolute or relative to working directory

4. **SSL certificate errors (Windows):**
   - Ensure `python-certifi-win32` is installed

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

**KumarGN**

## Acknowledgments

- Built with [Playwright](https://playwright.dev/)
- Powered by [Ollama](https://ollama.ai/)
- Inspired by Computer Use Agent (CUA) patterns

---

**Note:** This is an active development project. APIs and functionality may change.